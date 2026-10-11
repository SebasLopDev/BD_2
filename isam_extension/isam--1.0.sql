CREATE FUNCTION isam_build()
RETURNS integer
AS 'isam', 'isam_build'
LANGUAGE C;

CREATE FUNCTION isam_search(integer)
RETURNS text
AS 'isam', 'isam_search'
LANGUAGE C;

CREATE FUNCTION isam_insert(integer, text)
RETURNS void
AS 'isam', 'isam_insert'
LANGUAGE C;

CREATE FUNCTION isam_stats()
RETURNS text
AS 'isam', 'isam_stats'
LANGUAGE C;

CREATE FUNCTION isam_show_pages()
RETURNS text
AS 'isam', 'isam_show_pages'
LANGUAGE C;

CREATE FUNCTION isam_validate()
RETURNS text
AS 'isam', 'isam_validate'
LANGUAGE C;
