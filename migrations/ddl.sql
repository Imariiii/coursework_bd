CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE choirs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
);

CREATE TABLE conductors (
    id SERIAL PRIMARY KEY,
    choir_id INT NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (choir_id) REFERENCES choirs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE choir_members (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    choir_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (choir_id) REFERENCES choirs(id) ON DELETE CASCADE
);

CREATE TABLE choir_ranking (
    choir_id INT PRIMARY KEY,
    total_points INT NOT NULL,
    rank INT NOT NULL,
    FOREIGN KEY (choir_id) REFERENCES choirs(id) ON DELETE CASCADE
);

ALTER TABLE choir_ranking
DROP CONSTRAINT choir_ranking_choir_id_fkey,
ADD CONSTRAINT choir_ranking_choir_id_fkey
FOREIGN KEY (choir_id) REFERENCES choirs(id) ON DELETE CASCADE;

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE event_registrations (
    id SERIAL PRIMARY KEY,
    choir_id INT NOT NULL,
    event_id INT NOT NULL,
    points INT NOT NULL,
    FOREIGN KEY (choir_id) REFERENCES choirs(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

ALTER TABLE event_registrations
DROP CONSTRAINT event_registrations_event_id_fkey,
ADD CONSTRAINT event_registrations_event_id_fkey
FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION get_conductor_choirs(user_id INT)
RETURNS TABLE (id INT, name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name
    FROM choirs c
    JOIN conductors d ON c.id = d.choir_id
    WHERE d.user_id = get_conductor_choirs.user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_participant_choirs(user_id INT)
RETURNS TABLE (id INT, name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name
    FROM choirs c
    JOIN choir_members m ON c.id = m.choir_id
    WHERE m.user_id = get_participant_choirs.user_id;
END;
$$ LANGUAGE plpgsql;

CREATE VIEW choir_info AS
SELECT id, name, country
FROM choirs;

CREATE OR REPLACE VIEW choir_members_view AS
SELECT u.id, u.name, u.role, c.choir_id
FROM users u
JOIN choir_members c ON u.id = c.user_id
UNION
SELECT u.id, u.name, u.role, d.choir_id
FROM users u
JOIN conductors d ON u.id = d.user_id;

CREATE OR REPLACE VIEW conductor_choirs AS
SELECT c.id, c.name, d.user_id
FROM choirs c
JOIN conductors d ON c.id = d.choir_id;

CREATE VIEW choir_events AS
SELECT e.id, e.name, e.date, e.location, ce.choir_id
FROM events e
JOIN event_registrations ce ON e.id = ce.event_id;

CREATE OR REPLACE PROCEDURE create_choir(
    choir_name VARCHAR(255),
    choir_country VARCHAR(255),
    user_id INT
) AS $$
DECLARE
    choir_id INT;
BEGIN
    INSERT INTO choirs (name, country)
    VALUES (choir_name, choir_country)
    RETURNING id INTO choir_id;

    INSERT INTO conductors (choir_id, user_id)
    VALUES (choir_id, user_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_choir(IN choir_id INT)
AS $$
BEGIN
    DELETE FROM choirs WHERE id = delete_choir.choir_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_choir_related_data()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM choir_members WHERE choir_id = OLD.id;

    DELETE FROM conductors WHERE choir_id = OLD.id;

    DELETE FROM event_registrations WHERE choir_id = OLD.id;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_choir_delete
BEFORE DELETE ON choirs
FOR EACH ROW
EXECUTE FUNCTION delete_choir_related_data();

CREATE OR REPLACE FUNCTION is_choir_registered_for_event(
    choir_id INT,
    event_id INT
) RETURNS BOOLEAN AS $$
DECLARE
    registration_count INT;
BEGIN
    SELECT COUNT(*)
    INTO registration_count
    FROM event_registrations
    WHERE event_registrations.choir_id = is_choir_registered_for_event.choir_id  
      AND event_registrations.event_id = is_choir_registered_for_event.event_id; 

    RETURN registration_count > 0;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE add_member_to_choir(choir_id INT, user_id INT) AS $$
BEGIN
    INSERT INTO choir_members (choir_id, user_id)
    VALUES (choir_id, user_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE remove_member_from_choir(choir_id INT, user_id INT) AS $$
BEGIN
    DELETE FROM choir_members 
    WHERE choir_members.choir_id = remove_member_from_choir.choir_id AND 
          choir_members.user_id = remove_member_from_choir.user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE register_choir_for_event(choir_id INT, event_id INT) AS $$
BEGIN
    INSERT INTO event_registrations (choir_id, event_id)
    VALUES (choir_id, event_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE unregister_choir_from_event(choir_id INT, event_id INT) AS $$
BEGIN
    DELETE FROM event_registrations 
    WHERE event_registrations.choir_id = unregister_choir_from_event.choir_id AND 
          event_registrations.event_id = unregister_choir_from_event.event_id;
END;
$$ LANGUAGE plpgsql;