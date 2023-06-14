/*
Data migrations for:
  * 'knowledge' app

*/


-- CREATE EXTENSION dblink;
SELECT dblink_connect('hyllemath','host=localhost port=5432 dbname=hyllemath user=postgres password=postgres');



-- Knowledge / Biography / Map Packet --> InfoPacket + InfoItem + InfoItemVersion + InfoItemPosition
-- Knowledge / Biography / Map Packet  + Profile (acquired_by) --> InfoItemVersion + Knowledge

WITH imported AS (
  SELECT * FROM dblink(
    'hyllemath',
    $$
      SELECT id, title, text, author_id, 'knowledge'
      FROM knowledge_knowledgepacket kp
      UNION
      SELECT id, title, text, author_id, 'biography'
      FROM knowledge_biographypacket bp
      UNION
      SELECT id, title, '', NULL, 'map'
      FROM knowledge_mappacket bp
    $$)
    AS imported(id int, title text, text TEXT, author_id int, srctable text)
),
imported_new_ids AS (
  SELECT ROW_NUMBER () OVER() new_id,  *
  FROM imported
),
ins_infopackets AS (
  INSERT INTO infos_infopacket (id, title, infopacketkind)
  SELECT new_id, title, 'TEMP-0-GENERAL'
  FROM imported_new_ids
),
ins_infoitems AS (
  INSERT INTO infos_infoitem (id, title, isrestricted, enigmalevel, _createdat, _createdby_id)
  SELECT new_id, title, FALSE, 0, current_timestamp, author_id
  FROM imported_new_ids
),
ins_infoitemversions AS (
  INSERT INTO infos_infoitemversion (id, infoitem_id, versionkind, text, _createdat)
  SELECT new_id, new_id, '1. MAIN', TEXT, current_timestamp
  FROM imported_new_ids
),
ins_infoitemposition AS (
  INSERT INTO infos_infoitemposition (infoitem_id, infopacket_id, position)
  SELECT new_id, new_id, 1
  FROM imported_new_ids
),
contenttype AS (
  SELECT id FROM django_content_type
  WHERE model = 'infoitemversion'
  LIMIT 1
),
ins_knwoledgepacket_acquiredby AS (
  INSERT INTO characters_knowledge (isdirect, character_id, object_id, content_type_id)
  SELECT TRUE, profile_id, new_id, (SELECT id FROM contenttype)
  FROM dblink(
    'hyllemath',
    $$
      SELECT knowledgepacket_id, profile_id
      FROM knowledge_knowledgepacket_acquired_by
    $$)
    AS imported_acquiredby(packet_id int, profile_id int)
    JOIN imported_new_ids
      ON imported_new_ids.id = imported_acquiredby.packet_id
      AND imported_new_ids.srctable = 'knowledge'
),
ins_mappacket_acquiredby AS (
  INSERT INTO characters_knowledge (isdirect, character_id, object_id, content_type_id)
  SELECT TRUE, profile_id, new_id, (SELECT id FROM contenttype)
  FROM dblink(
    'hyllemath',
    $$
      SELECT mappacket_id, profile_id
      FROM knowledge_mappacket_acquired_by
    $$)
    AS imported_acquiredby(packet_id int, profile_id int)
    JOIN imported_new_ids
      ON imported_new_ids.id = imported_acquiredby.packet_id
      AND imported_new_ids.srctable = 'map'
),
ins_biographypacket_acquiredby AS (
  INSERT INTO characters_knowledge (isdirect, character_id, object_id, content_type_id)
  SELECT TRUE, profile_id, new_id, (SELECT id FROM contenttype)
  FROM dblink(
    'hyllemath',
    $$
      SELECT biographypacket_id, profile_id
      FROM knowledge_biographypacket_acquired_by
    $$)
    AS imported_acquiredby(packet_id int, profile_id int)
    JOIN imported_new_ids
      ON imported_new_ids.id = imported_acquiredby.packet_id
      AND imported_new_ids.srctable = 'knowledge'
)
SELECT 11  -- TODO dalsze inserty dla picture SETS z tych 3
;

SELECT setval('infos_infopacket_id_seq', 1 + (SELECT MAX(id) FROM infos_infopacket));
SELECT setval('infos_infoitem_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitem));
SELECT setval('infos_infoitemversion_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitemversion));
SELECT setval('infos_infoitemposition_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitemposition));
SELECT setval('characters_knowledge_id_seq', 1 + (SELECT MAX(id) FROM characters_knowledge));




-- KnowledgePacket + Reference --> InfoItemVersion + Reference

WITH imported AS (
  SELECT * FROM dblink(
    'hyllemath',
    $$
      SELECT r.id, title, description, url, kpr.knowledgepacket_id
      FROM knowledge_reference r
      JOIN knowledge_knowledgepacket_references kpr ON kpr.reference_id = r.id
    $$)
    AS imported(referenceid int, title text, description TEXT, url TEXT, knowledgepacketid int)
),
ins_references AS (
  INSERT INTO infos_reference (id, title, description, url)
  SELECT referenceid, title, description, url
  FROM imported
)
INSERT INTO infos_infoitemversion_references (infoitemversion_id, reference_id)
SELECT knowledgepacketid, referenceid
FROM imported;

SELECT setval('infos_reference_id_seq', 1 + (SELECT MAX(id) FROM infos_reference));
SELECT setval('infos_infoitemversion_references_id_seq', 1 + (SELECT MAX(id) FROM infos_infoitemversion_references));




-- Character + BiographyPacket --> CharacterVersion + InfoPacketSet (of InfoPackets made of BiographyPackets)

WITH imported AS (
  SELECT * FROM dblink(
    'hyllemath',
    $$
      SELECT cbp.character_id, c.fullname, bp.title
      FROM prosoponomikon_character_biography_packets cbp
      JOIN knowledge_biographypacket bp ON bp.id = cbp.biographypacket_id
      JOIN prosoponomikon_character c ON c.id = cbp.character_id
      ORDER BY c.fullname
    $$)
    AS imported(characterid int, fullname text, biographypackettitle TEXT)
),
ins_infopacketsets AS (
  INSERT INTO infos_infopacketset (title)
  SELECT DISTINCT fullname
  FROM imported
  RETURNING *
),
ins_infopacketset_infopackets AS (
  INSERT INTO infos_infopacketset_infopackets (infopacketset_id, infopacket_id)
  SELECT ips.id, ip.id
  FROM ins_infopacketsets ips
  JOIN imported ON imported.fullname = ips.title
  JOIN infos_infopacket ip ON ip.title = imported.biographypackettitle
  RETURNING *
)
UPDATE characters_characterversion
SET infopacketset_id = ips.id
FROM infos_infopacketset ips
WHERE versionkind = '2. MAIN' AND ips.title = fullname;

-- No need here for updates of id SEQUENCE, as defaults are in use.




DONE
knowledge_dialoguepacket
knowledge_knowledgepacket
knowledge_biographypacket
knowledge_mappacket
knowledge_knowledgepacket_acquired_by
knowledge_biographypacket_acquired_by
knowledge_mappacket_acquired_by

knowledge_reference
knowledge_knowledgepacket_references

prosoponomikon_character_biography_packets


TODO

knowledge_knowledgepacket_picture_sets
knowledge_biographypacket_picture_sets
knowledge_mappacket_picture_sets








-- ----------------------------------------------------------------------------
-- INFOS TODO:
/*
  1) knowledge_knowledgepacket_skills
  2) InfoItem - trzeba nadać 'enigmalevel', bo z defaultu wszędzie 0.
  3) KnowledgePackets, BiographyPackets i MapPackets z Hyllemath 1.0 są wrzucone w całości jako 1 InfoPacket z 1 InfoItem.
      Natomiast trzeba jeszcze wydzielić osobne InfoItem's z tego jednego.
      To będzie duża robota już na później, po migracji wszystkich danych. Być może zostawić ją w ogóle już na Hyllemath 2.0.
  4) Nie przenoszę tabeli "toponomikon_location_knowledge_packets" czyli powiązania KnowledgePacket do Location,
      a to dlatego, że InfoPacketSet-y dla LocationVersion trzeba będzie zbudować teraz od nowa.
      TODO: Trzeba oznaczyć sobie w osobnym widoku wszystkie "luźne" InfoPacket-y i InfoItem/Version, żeby wiedzieć,
            czeka na podpięcie i uporządkowanie.

*/


-- =====================================================

/*
TRUNCATE infos_infopacket CASCADE;
TRUNCATE infos_infoitem CASCADE;
TRUNCATE infos_infoitemposition CASCADE;
TRUNCATE characters_knowledge CASCADE;


*/

