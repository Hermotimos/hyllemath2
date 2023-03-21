/*
Data migrations for:
	* 'toponomikon' app

*/


CREATE EXTENSION dblink;
SELECT dblink_connect('hyllemath','host=localhost port=5432 dbname=hyllemath user=xxxxx password=yyyyy');





-- LocationType --> LocationType

WITH imported AS (
	SELECT * FROM dblink(
		'hyllemath',
		$$
			SELECT lt.id, name, name_plural, default_img_id, order_no, pi.image, pi.description
			FROM toponomikon_locationtype lt
			JOIN imaginarion_picture p ON p.id = lt.default_img_id
			JOIN imaginarion_pictureimage pi ON pi.id = p.image_id
		$$)
		AS imported(
			id int, name text, name_plural text, default_img_id int, order_no int,
			pictureimageurl TEXT, pictureimagedescription text)
),
ins_pictures AS (
  INSERT INTO resources_picture (title, category, image)
  SELECT DISTINCT ON (pictureimagedescription) pictureimagedescription, 'locationtype', pictureimageurl
  FROM imported
  RETURNING  *
)
INSERT INTO locations_locationtype (id, name, namepl, defaultpicture_id, hierarchynum)
SELECT imported.id, name, name_plural, ins_pictures.id, order_no
FROM imported
JOIN ins_pictures ON ins_pictures.image = imported.pictureimageurl;

SELECT setval('resources_picture_id_seq', 1 + (SELECT MAX(id) FROM resources_picture));
SELECT setval('locations_locationtype_id_seq', 1 + (SELECT MAX(id) FROM locations_locationtype));

SELECT * FROM locations_locationtype;




-- Location, PictureImage --> Location, LocationName, Picture, LocationVersion

WITH imported AS (
	SELECT * FROM dblink(
		'hyllemath',
		$$
			SELECT l.id, l.name, l.description, l.in_location_id, l.location_type_id, pi.image, pi.description,
				CASE WHEN l.name LIKE '% %' THEN NULL ELSE l.name END, 	-- propername
				CASE WHEN l.name LIKE '% %' THEN l.name ELSE NULL END 	-- descriptivename
			FROM toponomikon_location l
			JOIN imaginarion_picture p ON p.id = l.main_image_id
			JOIN imaginarion_pictureimage pi ON pi.id = p.image_id
		$$)
		AS imported(
			id int, name TEXT, description TEXT, in_location_id int, location_type_id int,
			pictureimageurl TEXT, pictureimagedescription TEXT,
			propername TEXT, descriptivename text)
),
ins_pictures AS (
  INSERT INTO resources_picture (title, category, image)
  SELECT DISTINCT ON (pictureimagedescription) pictureimagedescription, 'location', pictureimageurl
  FROM imported
  RETURNING  *
),
locationnames AS (
	INSERT INTO locations_locationname (nominative)
	SELECT DISTINCT propername
	FROM imported
	WHERE propername IS NOT NULL
	RETURNING id, nominative
),
ins_locations AS (
	INSERT INTO locations_location (id, _mainversionname, inlocation_id, locationtype_id, _createdat)
	SELECT imported.id, imported.name, imported.in_location_id, imported.location_type_id, current_timestamp
	FROM imported
	RETURNING *
),
ins_locationversions AS (
	INSERT INTO locations_locationversion (
		location_id, propername_id, descriptivename, name,
		versionkind, description, picture_id, _createdat)
	SELECT imported.id, locn.id, CASE WHEN imported.name LIKE '% %' THEN imported.name ELSE NULL END, imported.name,
		'1. MAIN', imported.description, pic.id, current_timestamp
	FROM imported
	LEFT JOIN locationnames locn ON locn.nominative = imported.name
	LEFT JOIN ins_pictures pic ON imported.pictureimageurl = pic.image
  RETURNING *
)
SELECT count(*) FROM ins_locationversions;

SELECT setval('resources_picture_id_seq', 1 + (SELECT MAX(id) FROM resources_picture));
SELECT setval('locations_location_id_seq', 1 + (SELECT MAX(id) FROM locations_location));
SELECT setval('locations_locationversion_id_seq', 1 + (SELECT MAX(id) FROM locations_locationversion));

SELECT * FROM locations_location ll;
SELECT * FROM locations_locationversion ll;




-- Location.participants, Location.informees ==> Knowledge (player-created) 3

WITH contenttype AS (
  SELECT id FROM django_content_type
  WHERE model = 'locationversion'
  LIMIT 1
),
imported AS (
  SELECT *
  FROM dblink(
    'hyllemath',
    $$
      SELECT location_id, profile_id, FALSE
      FROM toponomikon_location_informees
      UNION ALL
      SELECT location_id, profile_id, TRUE
      FROM toponomikon_location_participants
    $$)
    AS imported(location_id int, profileid int, is_direct boolean)
)
INSERT INTO characters_knowledge (isdirect, character_id, object_id, content_type_id)
SELECT DISTINCT ON (imported.location_id, profileid)
  is_direct, profileid, lver.id, (SELECT id FROM contenttype)
FROM imported JOIN locations_locationversion lver ON lver.location_id = imported.location_id
ORDER BY imported.location_id, profileid, is_direct DESC 	-- isdirect = TRUE FIRST: in case of duplicates take direct knowledge in DISTINCT ON
RETURNING *;

SELECT setval('characters_knowledge_id_seq', 1 + (SELECT MAX(id) FROM characters_knowledge));






-- ----------------------------------------------------------------------------
-- LOCATIONS TODO:
/*
  1) Dodać LocationNameTag i otagować nazwy istniejące. Następnie dodać te pospisywane, np. w MG TODO w Hyllemath 1.0


*/


-- =====================================================

/*
TRUNCATE resources_picture CASCADE;
TRUNCATE locations_locationtype CASCADE;
TRUNCATE locations_location CASCADE;


*/










