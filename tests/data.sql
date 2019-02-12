INSERT INTO user (username, password)
VALUES
	('test', 'test'),
	('other', ';alskdjf;akljg;alkdhjg');

INSERT INTO spot (note, author_id, created)
VALUES
	('test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');	