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
  SELECT DISTINCT ON (pictureimagedescription)
  	'[LOCATION TYPE] ' || pictureimagedescription, 'locationtypes', pictureimageurl
  FROM imported
  RETURNING  *
)
INSERT INTO locations_locationtype (id, name, namepl, defaultpicture_id, hierarchynum)
SELECT imported.id, name, name_plural, ins_pictures.id, order_no
FROM imported
JOIN ins_pictures ON ins_pictures.image = imported.pictureimageurl;

SELECT * FROM locations_locationtype;




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
  SELECT DISTINCT ON (pictureimagedescription)
  	'[LOCATION TYPE] ' || pictureimagedescription, 'locationtypes', pictureimageurl
  FROM imported
  RETURNING  *
)
INSERT INTO locations_locationtype (id, name, namepl, defaultpicture_id, hierarchynum)
SELECT imported.id, name, name_plural, ins_pictures.id, order_no
FROM imported
JOIN ins_pictures ON ins_pictures.image = imported.pictureimageurl;

SELECT setval('resources_picture_id_seq', 1 + (SELECT MAX(id) FROM resources_picture));
SELECT setval('locations_locationtype_id_seq', 1 + (SELECT MAX(id) FROM locations_locationtype));



-- TODO migracja LocationName utworzy?? je z Location.name. Niekt??re b??d?? "opisowe", np. Cierniowy Cypel, Wschodnia Rubie?? Hyllemath
-- TODO spr??bwa?? je wst??pnie przesia?? daj??c im atrybut "ispropername" = False (doda?? go na LocationName)
-- TODO wst??pny filtr po tym czy nazwa jest jednocz??onowa

-- TODO: zastanowi?? si?? nad dodaniem Location.throughlocations (plural!)
-- np. Akia.throughlocations = KirrDenurr, Wschoddnia Rubie??..., Skadia
-- Dolny Bieg Akii inlocation = Skadia, Wschodnia Rubie??... (bo graniczna rzeka)

-- Jak to zrobi??, ??eby niekt??re lokacje prezentowa?? jako graniczne, inne jako przechodz??ce przez wi??cej lokacji ??



-- =====================================================

/*
TRUNCATE resources_picture CASCADE;



*/










