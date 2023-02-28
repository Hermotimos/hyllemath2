
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

INSERT INTO characters_firstname (id, gender, nominative, genitive, description, firstnamegroup_id)
SELECT * FROM dblink(
	'hyllemath',
	$$
		SELECT fn.id, ag.type, form, 'TODO', COALESCE(form_2, ''), affix_group_id + 100    -- ids resulting from affix groups inflated to avoid repetitions
		FROM prosoponomikon_firstname AS fn
		JOIN prosoponomikon_affixgroup AS ag
			ON fn.affix_group_id = ag.id
	$$)
AS imported(id int, gender TEXT, nominative TEXT, genitive TEXT, description TEXT, firstnamegroup_id int);

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
				THEN nomina tive
			ELSE 'TODO'
		END);




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
FROM familyname_locations




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







-- ----------------------------------------------------------------------------
-- CHARACTERS TODO:
/*
	1) zamienić tagi będące nazwą Location na FirstName.locations M2M i tam zrobić update; tak samo FamilyName
			*** admin na zasadzie First/FamilyNameGroup z inline First/FamilyName z polami M2M do edycji w inlinie.
			*** możliwe Locations odfiltrować tylko te, które są krainami, żeby usprawnić wybór
*/





