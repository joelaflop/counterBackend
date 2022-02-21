drop function if exists last_updated_trigger;

CREATE FUNCTION last_updated_trigger() RETURNS trigger
   LANGUAGE plpgsql AS
$$BEGIN
   NEW.last_updated := current_timestamp;
   RETURN NEW;
END;$$;