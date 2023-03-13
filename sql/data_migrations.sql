
CREATE EXTENSION dblink;

SELECT dblink_connect('hyllemath','host=localhost port=5432 dbname=hyllemath user=xxxxx password=yyyyy');





-- User, Profile ==> User

INSERT INTO users_user (
    id, username, password, email, first_name, last_name,
    last_login, date_joined,
    is_superuser, is_staff, is_active, is_spectator
)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT DISTINCT ON (usr.id)
			usr.id, usr.username, usr.password, usr.email, '', '',
			usr.last_login, usr.date_joined,
			usr.is_superuser, usr.is_staff, prof.is_active, FALSE
		FROM auth_user AS usr
		JOIN users_profile AS prof
			ON usr.id = prof.user_id
		WHERE prof.status IN ('player', 'gm')		-- bez profili dla NPCów
		ORDER BY usr.id, prof.is_active DESC		-- Ludwik 2x profil (Marfan, Landar) -> zostaw jeden, aktywny
	$$)
AS imported(
    id int, username text, password text, email text, first_name text, last_name text,
	last_login timestamptz, date_joined timestamptz,
	is_superuser boolean, is_staff boolean, is_active boolean, is_spectator boolean);

/* TODO
	1) User.picture - add manually
	2) superuser stworzony pierwotnie w tej bazie - do usunięcia (pewnie 'lukasz' albo 'lukas')
*/




-- ==================================================================================
-- FIRST NAME

-- FirstNameGroup, AffixGroup ==> FirstNameGroup


INSERT INTO characters_firstnamegroup (id, title, description, parentgroup_id)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT id, title, TYPE, NULL
		FROM prosoponomikon_firstnamegroup
		UNION
		SELECT id + 100, affix, '', name_group_id			-- id + 100 to avoid repetiotions of id after JOIN
		FROM prosoponomikon_affixgroup
		ORDER BY 4 NULLS FIRST
	$$)
AS imported(id int, title text, description TEXT, name_group_id int);

SELECT setval('characters_familynamegroup_id_seq', 1 + (SELECT MAX(id) FROM characters_firstnamegroup));




-- AuxiliaryNameGroup ==> FirstNameTag

INSERT INTO characters_firstnametag (title, color)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT social_info, color
		FROM prosoponomikon_auxiliarynamegroup
		WHERE social_info IS NOT NULL AND social_info != ''
		UNION ALL
		SELECT loc.name, color
		FROM prosoponomikon_auxiliarynamegroup AS ang
		JOIN toponomikon_location AS loc ON loc.id = ang.location_id
		WHERE loc.name IS NOT NULL
	$$)
AS imported(social_info text, color TEXT);



-- FirstName ==> FirstName

INSERT INTO characters_firstname (
	id, gender, nominative, genitive, isarchaic, meaning, comments,
	origin_id, firstnamegroup_id)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT fn.id, ag.type, form, 'TODO', isarchaic, meaning, comments,
			origin_id,
			affix_group_id + 100    -- ids resulting from affix groups inflated to avoid repetitions
		FROM prosoponomikon_firstname AS fn
		JOIN prosoponomikon_affixgroup AS ag
			ON fn.affix_group_id = ag.id
	$$)
AS imported(
	id int, gender TEXT, nominative TEXT, genitive TEXT, isarchaic boolean, meaning TEXT, comments TEXT,
	origin_id int, firstnamegroup_id int);

SELECT setval('characters_firstname_id_seq', 1 + (SELECT MAX(id) FROM characters_firstname));


-- Utwórz formy dopełniacza
UPDATE characters_firstname
	SET genitive = (
		CASE
			WHEN gender = 'MALE' AND nominative ~ '[bcdfghjklmnpqrstvwxz]$'
				THEN nominative || 'a'
			WHEN gender = 'FEMALE' AND nominative ~ '[eiy]a$'
				THEN LEFT(nominative, LENGTH(nominative)-1) || 'i'
			WHEN gender = 'FEMALE' AND nominative ~ '[bcdfghjklmnpqrstvwxz]a$'
				THEN LEFT(nominative, LENGTH(nominative)-1) || 'y'
			WHEN gender = 'FEMALE'
				THEN nominative
			ELSE 'TODO'
		END);




-- FirstName M2M equivalents ==> FirstName M2M equivalents

INSERT INTO characters_firstname_equivalents (id, from_firstname_id, to_firstname_id)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT id, from_firstname_id, to_firstname_id
		FROM prosoponomikon_firstname_equivalents
	$$)
AS imported(id int, from_firstname_id int, to_firstname_id int);




-- FK AuxiliaryNameGroup + FirstName ==> FirstNameTag + FirstName

INSERT INTO characters_firstname_tags (firstname_id , firstnametag_id)
SELECT imported.firstname_id, fnt.id
FROM dblink(
	'hyllemath',
	$$
		SELECT fn.id AS firstname_id, tags.tag_title
		FROM (
			SELECT id, social_info AS tag_title, color
			FROM prosoponomikon_auxiliarynamegroup
			WHERE social_info IS NOT NULL AND social_info != ''
			UNION ALL
			SELECT ang.id, loc.name, color
			FROM prosoponomikon_auxiliarynamegroup AS ang
			JOIN toponomikon_location AS loc ON loc.id = ang.location_id
			WHERE loc.name IS NOT NULL
		) AS tags
		JOIN prosoponomikon_firstname fn ON fn.auxiliary_group_id = tags.id
	$$)
AS imported(firstname_id int, tag_title text)
JOIN characters_firstnametag fnt ON imported.tag_title = fnt.title;




-- ==================================================================================
-- FAMILY NAME


-- FamilyNameGroup ==> FamilyNameGroup

INSERT INTO characters_familynamegroup (id, title, description)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT id, title, description
		FROM prosoponomikon_familynamegroup
	$$)
AS imported(id int, title text, description TEXT);




-- M2M FamilyName+Location ==> FamilyNameTag

WITH familyname_locations AS (
	SELECT * FROM dblink(
		'hyllemath',
		$$
			SELECT fn.form, l.name
			FROM prosoponomikon_familyname fn
			JOIN prosoponomikon_familyname_locations fnl ON fnl.familyname_id = fn.id
			JOIN toponomikon_location l ON l.id = fnl.location_id
		$$)
	AS imported(familyname TEXT, locationname text))
INSERT INTO characters_familynametag (title, color)
SELECT DISTINCT locationname, '#000000'
FROM familyname_locations;




-- FamilyName ==> FamilyName

INSERT INTO characters_familyname (
	id, nominative, nominative_pl, genitive, genitive_pl, description, familynamegroup_id)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT fn.id, form, 'TODO', 'TODO', 'TODO', COALESCE(info, ''), group_id
		FROM prosoponomikon_familyname AS fn
	$$)
AS imported(
	id int, nominative TEXT, nominative_pl TEXT, genitive TEXT, genitive_pl TEXT,
	description TEXT, familynamegroup_id int);

SELECT setval('characters_familyname_id_seq', 1 + (SELECT MAX(id) FROM characters_familyname));



-- Utwórz formy dopełniacza i liczby mnogiej
UPDATE characters_familyname
	SET
		nominative_pl = CASE
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]o$'
				THEN nominative
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]$'
				THEN nominative || 'owie'
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]a$'
				THEN LEFT(nominative, LENGTH(nominative)-1) || 'owie'
			ELSE 'TODO'
		END,
		genitive = CASE
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]o$'
				THEN nominative
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]a$'
				THEN LEFT(nominative, LENGTH(nominative)-1) || 'i'
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]$'
				THEN nominative || 'a'
			ELSE 'TODO'
		END,
		genitive_pl  = CASE
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]o$'
				THEN nominative
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]$'
				THEN nominative || 'ów'
			WHEN nominative ~ '[bcdfghjklmnpqrstvwxz]a$'
				THEN LEFT(nominative, LENGTH(nominative)-1) || 'ów'
			ELSE 'TODO'
		END;




-- FamilyName + Locations ==> FamilyName + FamilyNameTag

INSERT INTO characters_familyname_tags (familyname_id, familynametag_id)
SELECT DISTINCT fn.id, fnt.id
FROM dblink(
	'hyllemath',
	$$
		SELECT fn.form, l.name
		FROM prosoponomikon_familyname fn
		JOIN prosoponomikon_familyname_locations fnl ON fnl.familyname_id = fn.id
		JOIN toponomikon_location l ON l.id = fnl.location_id
	$$)
	AS imported(familyname TEXT, locationname text)
JOIN characters_familynametag fnt ON fnt.title = imported.locationname
JOIN characters_familyname fn ON fn.nominative = imported.familyname;







-- ==================================================================================
-- CHARACTERS / CHARACTER VERSIONS


WITH
imported AS (
	SELECT *
	FROM dblink(
		'hyllemath',
		$$
			SELECT p.id AS profileid, p.image, p.is_alive, p.user_id AS userid,
				c.id AS characterid, c.first_name_id, c.family_name_id, c.cognomen, c.fullname, c.description,
				c.strength, c.dexterity, c.endurance, c.experience, c.created_by_id, createdby.user_id AS createdbyuserid
			FROM prosoponomikon_character c
			JOIN users_profile p ON p.id = c.profile_id
			LEFT JOIN users_profile createdby ON createdby.id = c.created_by_id
			WHERE p.id != 1 	-- exclude GM character
		$$)
		AS imported(
				profileid int, image text, is_alive boolean, userid int,
				characterid int, first_name_id int, family_name_id int, cognomen text, fullname text, description text,
				strength int, dexterity int, endurance int, experience int, created_by_id int, createdbyuserid int)
)
,
ins_characters AS (
	INSERT INTO characters_character (id, user_id, _createdat)
	SELECT profileid, userid, current_timestamp 										-- characters have ids from profiles
	FROM imported
	RETURNING *
),
ins_pictures AS (
	INSERT INTO resources_picture (title, category, image)
	SELECT REPLACE(REPLACE(image, 'profile_pics/profile_', ''), '_', ' '), 'characters', image
	FROM imported
	WHERE image != 'profile_pics/profile_default.jpg'
	RETURNING  *
)
INSERT INTO characters_characterversion (
	id, character_id, versionkind, isalive, isalterego, firstname_id, familyname_id,
	nickname, originname, fullname,
	description, strength, dexterity, endurance, power, experience,
	_createdby_id, _createdat, picture_id
)
SELECT characterid, profileid, '2. MAIN', is_alive, FALSE, first_name_id, family_name_id,
	CASE WHEN cognomen LIKE 'z %' OR cognomen LIKE 'ze %' THEN NULL ELSE cognomen END,
	CASE WHEN cognomen LIKE 'z %' OR cognomen LIKE 'ze %' THEN cognomen ELSE NULL END, fullname,
	description, strength, dexterity, endurance, 0, experience,
	createdbyuserid, current_timestamp , pic.id
FROM imported
LEFT JOIN ins_pictures pic ON pic.image = imported.image;			-- LEFT dla postaci bez obrazka: utworzone przez graczy lub niedokończone


SELECT setval('characters_character_id_seq', 1 + (SELECT MAX(id) FROM characters_character));
SELECT setval('characters_characterversion_id_seq', 1 + (SELECT MAX(id) FROM characters_characterversion));





/*
IMPORTANT:
		* Profile.id 			----> 	Character.id
		* Character.id 		-----> 	CharacterVersion.id
*/


-- all 9143 minus GM 395 = 9748

-- Acquaitanceship ==> Knowledge (non-AKA) 8727

WITH contenttype AS (
	SELECT id FROM django_content_type
	WHERE model = 'characterversion'
	LIMIT 1
)
INSERT INTO characters_knowledge (id, isdirect, character_id, object_id, content_type_id)
SELECT id, is_direct, profileid, known_character_id, (SELECT id FROM contenttype)
FROM dblink(
	'hyllemath',
	$$
		SELECT a.id, a.is_direct, a.knowing_character_id, a.known_character_id,
			knowing.id, knowing.profile_id, knowing.fullname
		FROM prosoponomikon_acquaintanceship a
		JOIN prosoponomikon_character knowing ON knowing.id = knowing_character_id
		JOIN prosoponomikon_character known ON known.id = known_character_id
		WHERE knowing.profile_id != 1																		-- nie rób Knowledge dla MG
			AND known.created_by_id IS NULL															-- odfiltruj player-created
			AND (a.knows_as_name = '') IS NOT FALSE 									-- odfiltruj "AKA" (te gdzie nie-null i nie '')
			AND (a.knows_as_description = '') IS NOT FALSE
			AND (a.knows_as_image = '') IS NOT FALSE
	$$)
	AS imported(
	id int, is_direct boolean, knowing_character_id int, known_character_id int,
	characterid int, profileid int, fullname text);


SELECT setval('characters_knowledge_id_seq', 1 + (SELECT MAX(id) FROM characters_knowledge));




-- Acquaitanceship AKA ==> Knowledge + CharacterVersion(for AKA) 18


-- Create Picture objects for AKA with alternative pics
INSERT INTO resources_picture (title, category, image)
SELECT DISTINCT REPLACE(REPLACE(knows_as_image, 'profile_pics/profile_', ''), '_', ' '), 'characters', knows_as_image
FROM dblink(
	'hyllemath',
	$$
		SELECT knows_as_image
		FROM prosoponomikon_acquaintanceship
		WHERE knows_as_image != ''
	$$)
	AS imported(knows_as_image TEXT)
ON CONFLICT (title) DO NOTHING;



WITH contenttype AS (
	SELECT id FROM django_content_type
	WHERE model = 'characterversion'
	LIMIT 1
),
imported AS (
	SELECT * --id, is_direct, profileid, known_character_id
	FROM dblink(
		'hyllemath',
		$$
			SELECT a.id acquaintanceshipid, a.is_direct,
				a.knowing_character_id, knowing.profile_id, knowing.fullname knowing_fullname,
				a.known_character_id, known.fullname known_fullname, known.profile_id known_profileid,
				a.knows_as_name, a.knows_as_description, a.knows_as_image
			FROM prosoponomikon_acquaintanceship a
			JOIN prosoponomikon_character knowing ON knowing.id = knowing_character_id
			JOIN prosoponomikon_character known ON known.id = known_character_id
			WHERE knowing.profile_id != 1																															-- nie rób Knowledge dla MG
				AND known.created_by_id IS NULL																													-- odfiltruj player-created
				AND (a.knows_as_name != '' OR a.knows_as_description != '' OR a.knows_as_image != '' ) 	-- weź tylko "AKA" (te gdzie nie-null i nie '')
		$$)
		AS imported(
			acquaintanceshipid int, is_direct boolean,
			knowing_character_id int, profileid int, knowing_fullname TEXT,
			known_character_id int, known_fullname TEXT, known_profileid int,
			knows_as_name TEXT, knows_as_description TEXT, knows_as_image TEXT)
),
inserted AS (
	INSERT INTO characters_characterversion (
		id, character_id, versionkind, isalive, isalterego, firstname_id, familyname_id,
		nickname, originname, fullname,
		description, _createdat, picture_id
	)
	SELECT DISTINCT ON (knows_as_name, knows_as_description, knows_as_image)
		nextval('characters_character_id_seq'), known_profileid, '4. PARTIAL', TRUE, FALSE, NULL, NULL,
		split_part(knows_as_name, ' z ', 1),
		CASE WHEN split_part(knows_as_name, ' z ', 2) != '' THEN 'z ' || split_part(knows_as_name, ' z ', 2) ELSE '' END,
		CASE WHEN knows_as_name != '' THEN knows_as_name ELSE chv.fullname END,
		CASE WHEN knows_as_description != '' THEN knows_as_description ELSE chv.description END,
		current_timestamp , COALESCE(pic.id, chv.picture_id)
	FROM imported JOIN characters_characterversion chv ON imported.known_character_id = chv.id
	LEFT JOIN resources_picture pic ON pic.image = imported.knows_as_image
	RETURNING *
) --SELECT * FROM inserted
INSERT INTO characters_knowledge (id, isdirect, character_id, object_id, content_type_id)
SELECT DISTINCT ON ((knowing_character_id, profileid, known_fullname))
	nextval('characters_knowledge_id_seq'), is_direct, profileid, ins.id, (SELECT id FROM contenttype)
FROM imported imp JOIN inserted ins ON imp.known_profileid = ins.character_id
RETURNING *;



-- Acquaitanceship ==> Knowledge (player-created) 3

WITH contenttype AS (
	SELECT id FROM django_content_type
	WHERE model = 'characterversion'
	LIMIT 1
), inserted AS (
	INSERT INTO characters_knowledge (id, isdirect, character_id, object_id, content_type_id)
	SELECT id, is_direct, createdbyid, known_character_id, (SELECT id FROM contenttype)
	FROM dblink(
		'hyllemath',
		$$
			SELECT a.id, a.is_direct, a.knowing_character_id, a.known_character_id,
				known.id, known.profile_id, known.fullname, known.created_by_id
			FROM prosoponomikon_acquaintanceship a
			JOIN prosoponomikon_character knowing ON knowing.id = knowing_character_id
			JOIN prosoponomikon_character known ON known.id = known_character_id
			WHERE known.created_by_id IS NOT NULL							-- tylko player-created
				AND knowing_character_id != 30							-- nie rób Knowledge dla MG
		$$)
		AS imported(
			id int, is_direct boolean, knowing_character_id int, known_character_id int,
			characterid int, profileid int, fullname TEXT, createdbyid int)
	RETURNING *
)
UPDATE characters_characterversion c
SET versionkind = '6. BYPLAYER'
FROM inserted
WHERE c.id = inserted.object_id;


SELECT setval('characters_knowledge_id_seq', 1 + (SELECT MAX(id) FROM characters_knowledge));








-- ----------------------------------------------------------------------------
-- CHARACTERS TODO:
/*
	1) zamienić tagi będące nazwą Location na FirstName.locations M2M i tam zrobić update; tak samo FamilyName
			*** admin na zasadzie First/FamilyNameGroup z inline First/FamilyName z polami M2M do edycji w inlinie.
			*** możliwe Locations odfiltrować tylko te, które są krainami, żeby usprawnić wybór
	2) [???] zrobić wersje z isalterego=True (Hagadon, Farkon itd.)
	3) Skopiować wszystkie media/ pliki, zamienić Total Commanderem " " na "_" spacja na podkreślenia


*/


/*

TRUNCATE characters_familyname CASCADE;
TRUNCATE characters_firstname CASCADE;
TRUNCATE characters_familynamegroup CASCADE;
TRUNCATE characters_firstnamegroup CASCADE;
TRUNCATE characters_familynametag  CASCADE;
TRUNCATE characters_firstnametag  CASCADE;
TRUNCATE users_user CASCADE;
TRUNCATE resources_picture CASCADE;

*/