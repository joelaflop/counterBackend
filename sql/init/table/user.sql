drop table if exists "user";
create table "user"
(
    id           serial primary key,
    username     varchar(255) unique,
    firstname    varchar(63),
    lastname     varchar(63),
    first_login  timestamptz,
    last_login   timestamptz,
    logins       integer,
    timezone     varchar(63),
    password     varchar(255),
    last_updated timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TRIGGER update_user_last_updated
    BEFORE UPDATE
    ON "user"
    FOR EACH ROW
EXECUTE PROCEDURE last_updated_trigger();
