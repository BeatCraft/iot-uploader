CREATE TABLE upload_counts (
    id INT NOT NULL AUTO_INCREMENT,
    sensor_name TEXT,
    date DATE,
    hour INT,
    count INT DEFAULT 0,
    timestamp TIMESTAMP,
    PRIMARY KEY (id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE INDEX ix_upload_date on upload_counts(date);

