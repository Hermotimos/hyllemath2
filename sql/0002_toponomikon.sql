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
ins AS (
	INSERT INTO locations_location (id, propername_id, descriptivename, name, inlocation_id, locationtype_id)
	SELECT imported.id, locn.id, CASE WHEN imported.name LIKE '% %' THEN imported.name ELSE NULL END, imported.name,
		imported.in_location_id, imported.location_type_id
	FROM imported
	LEFT JOIN locationnames locn ON locn.nominative = imported.name
	RETURNING *)
SELECT count(*) FROM ins;

SELECT setval('resources_picture_id_seq', 1 + (SELECT MAX(id) FROM resources_picture));
SELECT setval('locations_location_id_seq', 1 + (SELECT MAX(id) FROM locations_location));

SELECT * FROM locations_location ll;






-- =====================================================

/*
TRUNCATE resources_picture CASCADE;
TRUNCATE locations_locationtype CASCADE;
TRUNCATE locations_location CASCADE;


*/










