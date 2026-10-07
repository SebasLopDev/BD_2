CREATE FUNCTION isam_build()
RETURNS integer
AS 'isam', 'isam_build'
LANGUAGE C;

CREATE FUNCTION isam_search(integer)
RETURNS text
AS 'isam', 'isam_search'
LANGUAGE C;
