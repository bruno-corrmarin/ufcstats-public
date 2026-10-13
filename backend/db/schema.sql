CREATE TABLE fighters (
    fighter_id      CHAR(16)      UNIQUE PRIMARY KEY,
    first_name      VARCHAR(50),
    last_name       VARCHAR(50),
    nickname        VARCHAR(50),
    height          INTEGER,
    weight          INTEGER,
    reach           DECIMAL(4,1),
    stance          VARCHAR(20),
    wins            INTEGER,
    losses          INTEGER,
    draws           INTEGER   

);

CREATE TABLE fights (
    fight_id        SERIAL          PRIMARY KEY,
    fighter1_id     CHAR(16)        REFERENCES fighters(fighter_id),
    fighter2_id     CHAR(16)        REFERENCES fighters(fighter_id),
    winner_id       CHAR(16)        REFERENCES fighters(fighter_id),
    method          VARCHAR(50),
    round           INTEGER,
    time            VARCHAR(10),
    date            DATE
);