drop table if exists "oauth2";
create table "oauth2"
(
    id            serial primary key,
    user_id       integer NOT NULL,
    token_type    varchar(31),
    api_name      varchar(31),
    access_token  varchar(255),
    refresh_token varchar(255),
    received      timestamptz,
    expiry        timestamptz,
    last_updated  timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT oauth2_fk foreign key (user_id) references "user"(id)
);

CREATE TRIGGER update_oauth2_last_updated
    BEFORE UPDATE
    ON "oauth2"
    FOR EACH ROW
EXECUTE PROCEDURE last_updated_trigger();

CREATE INDEX oauth2_access_token_idx ON "oauth2" (access_token);
