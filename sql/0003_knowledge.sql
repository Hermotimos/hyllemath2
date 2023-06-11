/*
Data migrations for:
	* 'knowledge' app

*/


-- CREATE EXTENSION dblink;
SELECT dblink_connect('hyllemath','host=localhost port=5432 dbname=hyllemath user=postgres password=postgres');



-- KnowledgePacket --> InfoPacket + InfoItem

WITH imported AS (
	SELECT * FROM dblink(
		'hyllemath',
		$$
			SELECT id, title, text, author_id
			FROM knowledge_knowledgepacket
		$$)
		AS imported(id int, title text, text TEXT, author_id int)
),
ins_infopackets AS (
  INSERT INTO infos_infopacket (id, title, infopacketkind)
  SELECT id, title, 'TEMP-0-GENERAL'
  FROM imported
  RETURNING  *
),
ins_infoitems AS (
	INSERT INTO infos_infoitem (id, title, isrestricted, enigmalevel, _createdat, _createdby_id)
	SELECT id, title, FALSE, 0, current_timestamp, author_id
	FROM imported
	RETURNING *
)
INSERT INTO infos_infoitemposition (infoitem_id, infopacket_id, position)
SELECT id, id, 1
FROM imported;

SELECT setval('infos_infopacket_id_seq', 1 + (SELECT MAX(id) FROM infos_infopacket));
SELECT setval('infos_infoitem_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitem));
SELECT setval('infos_infoitemposition_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitemposition));







DONE
knowledge_dialoguepacket
knowledge_knowledgepacket


TODO

knowledge_knowledgepacket_acquired_by
knowledge_knowledgepacket_picture_sets
knowledge_knowledgepacket_references
knowledge_knowledgepacket_skills

knowledge_biographypacket
knowledge_biographypacket_acquired_by
knowledge_biographypacket_picture_sets
prosoponomikon_character_biography_packets

knowledge_mappacket
knowledge_mappacket_acquired_by
knowledge_mappacket_picture_sets
knowledge_reference



-- ----------------------------------------------------------------------------
-- INFOS TODO:
/*
 	1) InfoItem - trzeba nadać 'enigmalevel', bo z defaultu wszędzie 0.
  2) KnowledgePackets, BiographyPackets i MapPackets z Hyllemath 1.0 są wrzucone w całości jako 1 InfoPacket z 1 InfoItem.
  		Natomiast trzeba jeszcze wydzielić osobne InfoItem's z tego jednego.
  		To będzie duża robota już na później, po migracji wszystkich danych. Być może zostawić ją w ogóle już na Hyllemath 2.0.


*/


-- =====================================================

/*
TRUNCATE infos_infopacket CASCADE;
TRUNCATE infos_infoitem CASCADE;
TRUNCATE infos_infoitemposition CASCADE;


*/

