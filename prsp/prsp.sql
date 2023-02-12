CREATE SCHEMA IF NOT EXISTS prsp;

/*
NOTES:
    Table field types:
    - always TEXT for textual data, as it is faster in Postgres than CHAR(n) and VARCHAR(n);
      But as the lenght of text written into the db should not be left uncontrolled, move it to the Python layer (Django or dataclasses or else)

    - use INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY instead of SERIAL PRIMARY KEY
        This prevents insert of non-sequential values and is in accordance with SQL standard

*/


-- ==========================================


CREATE TABLE prsp.FirstNameGroup (
  id INT GENERATED BY DEFAULT AS IDENTITY,
  firstnamegroupid INT,
  title TEXT NOT NULL, -- max 100   // 1st level: affix ex. *-os/*-as // 2nd level: Location
  description TEXT,  -- max 10000
  -- ---------------------
  CONSTRAINT prsp_firstnamegroup_pk                 PRIMARY KEY (id),
  CONSTRAINT prsp_firstnamegroup_firstnamegroup_fk  FOREIGN KEY (firstnamegroupid) REFERENCES prsp.FirstNameGroup(id),
  CONSTRAINT prsp_firstnamegroup_title_uq           UNIQUE (title)
);
CREATE INDEX prsp_firstnamegroup_firstnamegroupid_ix ON prsp.FirstNameGroup USING btree (firstnamegroupid);


CREATE TABLE prsp.FirstName (
  id INT GENERATED BY DEFAULT AS IDENTITY,
	firstnamegroupid INT NOT NULL,
  originid INT,
	nominative TEXT NOT NULL, -- max 50
	genitive TEXT,  -- max 50
	oldform TEXT, -- max 50
	info TEXT,  -- max 10000
  -- ---------------------
  CONSTRAINT prsp_firstname_pk                PRIMARY KEY (id),
  CONSTRAINT prsp_firstname_firstnamegroup_fk FOREIGN KEY (firstnamegroupid) REFERENCES prsp.FirstNameGroup(id),
  CONSTRAINT prsp_firstname_origin_fk         FOREIGN KEY (originid) REFERENCES prsp.FirstName(id),
  CONSTRAINT prsp_firstname_nominative_uq     UNIQUE (nominative)
);
CREATE INDEX prsp_firstname_firstnamegroupid_ix ON prsp.FirstName USING btree (firstnamegroupid);
CREATE INDEX prsp_firstname_originid_ix         ON prsp.FirstName USING btree (originid);


-- ==========================================


CREATE TABLE prsp.FamilyNameGroup (
  id INT GENERATED BY DEFAULT AS IDENTITY,
  familynamegroupid INT,
  title TEXT NOT NULL, -- max 100
  description TEXT,  -- max 10000
  -- ---------------------
  CONSTRAINT prsp_familynamegroup_pk                  PRIMARY KEY (id),
  CONSTRAINT prsp_familynamegroup_familynamegroup_fk  FOREIGN KEY (familynamegroupid) REFERENCES prsp.FamilyNameGroup(id),
  CONSTRAINT prsp_familynamegroup_title_uq            UNIQUE (title)
);
CREATE INDEX prsp_familynamegroup_familynamegroupid_ix ON prsp.FamilyNameGroup USING btree (familynamegroupid);


CREATE TABLE prsp.FamilyName (
  id INT GENERATED BY DEFAULT AS IDENTITY,
	familynamegroupid INT NOT NULL,
  originid INT,
	nominative TEXT NOT NULL, -- max 50
	nominative_pl TEXT NOT NULL, -- max 50
	genitive TEXT,  -- max 50
	genitive_pl TEXT,  -- max 50
	oldform TEXT, -- max 50
	info TEXT,  -- max 10000
  -- ---------------------
  CONSTRAINT prsp_familyname_pk                 PRIMARY KEY (id),
  CONSTRAINT prsp_familyname_familynamegroup_fk FOREIGN KEY (familynamegroupid) REFERENCES prsp.FamilyNameGroup(id),
  CONSTRAINT prsp_familyname_origin_fk          FOREIGN KEY (originid) REFERENCES prsp.FamilyName(id),
  CONSTRAINT prsp_familyname_nominative_uq      UNIQUE (nominative)
);
CREATE INDEX prsp_familyname_familynamegroupid_ix ON prsp.FamilyName USING btree (familynamegroupid);
CREATE INDEX prsp_familyname_originid_ix          ON prsp.FamilyName USING btree (originid);


-- ==========================================


CREATE TABLE prsp.Character (
  id INT GENERATED BY DEFAULT AS IDENTITY,
  userid INT NOT NULL,
  firstnameid INT,
  familynameid INT,
  nickname TEXT, -- max 50
  originname TEXT, -- max 50
  _info TEXT, -- max 2000: pole na dodatkową informację do wyświetlenia w __str__ dla "wersji"
  -- ---------------------
  CONSTRAINT prsp_character_pk            PRIMARY KEY (id),
  CONSTRAINT prsp_character_user_fk       FOREIGN KEY (userid) REFERENCES public.Users_User(id),
  CONSTRAINT prsp_character_firstname_fk  FOREIGN KEY (firstnameid) REFERENCES prsp.FirstName(id),
  CONSTRAINT prsp_character_familyname_fk FOREIGN KEY (familynameid) REFERENCES prsp.FamilyName(id)
);
CREATE INDEX prsp_character_userid_ix       ON prsp.Character USING btree (userid);
CREATE INDEX prsp_character_firstnameid_ix  ON prsp.Character USING btree (firstnameid);
CREATE INDEX prsp_character_familynameid_ix ON prsp.Character USING btree (familynameid);

-- TODO 1: CharacterVersion
  -- Zastanowić się nad Character vs. CharacterVersion

  -- 1) POMYŚLEĆ NAD TYM OD STRONY GRACZA który chce ukrywać swoją tożsamość przed innymi: robi swoje alterego
  -- 2) POMYSLEĆ TEŻ CO BĘDZIE PROSTSZE W UTRZYMANIU - chyba jedna tabela z polami 'identityid' / 'ofcharacterid' FK Character (self FK)

  -- redundancja danych i tak jest wpisana w wersje - żeby nie były powtarzane mechanizm bardzo skomplikowany i trudny w zarządzaniu

  -- ponadto jak np. jakiś szpieg ma 3 oblicza, to będzie występował po 1, 2 czy 3 w wydarzeniach, lokacjach i Prosoponomikonie;;
      -- trzeba dać Graczom możliwość ujednolicania tożsamości - osobna tabela gdzie mogliby określać które CharacterVersion.id uznają za tożsame (jedną Postać)
      -- ale to już mega skomplikowane - pomyślec nad jakichś mechanizmem może nie-programistycznym tylko administracyjnym



-- TODO 2: Tags, TagGroups (1 - Gender, 2 - Social, 3 - Local, 4 - Racial):
-- Tag.taggroupid, TagGroup.authorid - Gracz ma dostęp do Tagów należący do TagGroup których jest autorem + gdzie authorid NULL (=defaultowe)


-- TODO 3: jak już będzie Toponomikon: FirstNameToLocationLink, FamilyNameToLocationLink:
--    dzięki nim wyświetlanie po lokacjach i możliwość randomowego generowania FirstName+LastName, FirstName+[OriginName based on Location] ex. Aos z Keii