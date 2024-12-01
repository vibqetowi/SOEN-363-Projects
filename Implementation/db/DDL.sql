CREATE TABLE Disaster (
    id          SERIAL PRIMARY KEY,
    time        TIMESTAMP      NOT NULL,
    type        VARCHAR(50)    NOT NULL,
    latitude    DECIMAL(9, 6)  NOT NULL,
    longitude   DECIMAL(9, 6)  NOT NULL,
    modified_on TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_coordinates CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
);

CREATE TABLE Earthquake (
    disaster_id INT PRIMARY KEY,
    depth DECIMAL(5, 2) NOT NULL,
    magnitude DECIMAL(3, 1) NOT NULL CHECK (magnitude >= 0 AND magnitude <= 10),
    CONSTRAINT fk_earthquake_disaster FOREIGN KEY (disaster_id) REFERENCES Disaster (id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION update_modified_on()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_on := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_takes_modtime
BEFORE UPDATE ON Disaster
FOR EACH ROW
EXECUTE FUNCTION update_modified_on();

CREATE OR REPLACE FUNCTION earthquake_update_disaster()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Disaster
    SET modified_on = CURRENT_TIMESTAMP
    WHERE id = NEW.disaster_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER earthquake_update_disaster_trigger
AFTER UPDATE ON Earthquake
FOR EACH ROW
EXECUTE FUNCTION earthquake_update_disaster();
