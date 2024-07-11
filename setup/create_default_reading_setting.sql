CREATE TABLE default_reading_settings (
    id INT NOT NULL AUTO_INCREMENT,
    camera_id TEXT,
    sensor_name TEXT,
    reading_setting_id INT,
    timestamp TIMESTAMP,
    PRIMARY KEY (id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

