drop table if exists "listen";
create table "listen"
(
    id            serial primary key,
    user_id       integer                               NOT NULL,
    recorded      timestamptz,
    api_name      varchar(31),
    api_id        varchar(255),
    api_timestamp timestamptz,
    duration      interval,
    title         varchar(255),
    album         varchar(255),
    artists       varchar(1023),
    last_updated  timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT listen_fk foreign key (user_id) references "user" (id)
);

CREATE TRIGGER update_listen_last_updated
    BEFORE UPDATE
    ON "listen"
    FOR EACH ROW
EXECUTE PROCEDURE last_updated_trigger();
