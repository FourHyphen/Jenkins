CREATE TABLE PopTbl (
    pref_name VARCHAR(20) PRIMARY KEY NOT NULL,
    population INTEGER
);

INSERT INTO PopTbl (pref_name, population) VALUES('徳島', 100);
INSERT INTO PopTbl (pref_name, population) VALUES('香川', 200);
INSERT INTO PopTbl (pref_name, population) VALUES('愛媛', 150);
INSERT INTO PopTbl (pref_name, population) VALUES('高知', 200);
INSERT INTO PopTbl (pref_name, population) VALUES('福岡', 300);
INSERT INTO PopTbl (pref_name, population) VALUES('佐賀', 100);
INSERT INTO PopTbl (pref_name, population) VALUES('長崎', 200);
INSERT INTO PopTbl (pref_name, population) VALUES('東京', 400);
INSERT INTO PopTbl (pref_name, population) VALUES('群馬',  50);

SELECT * FROM PopTbl;
