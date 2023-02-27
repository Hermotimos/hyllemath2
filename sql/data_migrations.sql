
CREATE EXTENSION dblink;

SELECT dblink_connect('hyllemath','host=localhost port=5432 dbname=hyllemath user=xxxxxxx password=yyyyyy');





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
AS userprofile(
    id int, username text, password text, email text, first_name text, last_name text,
	last_login timestamptz, date_joined timestamptz,
	is_superuser boolean, is_staff boolean, is_active boolean, is_spectator boolean);

/* TODO
	1) User.picture - add manually
	2) superuser stworzony pierwotnie w tej bazie - do usunięcia (pewnie 'lukasz' albo 'lukas')
*/

