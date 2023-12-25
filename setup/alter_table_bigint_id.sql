# uploads.id

#ALTER TABLE sensor_data DROP FOREIGN KEY sensor_data_ibfk_1;
#ALTER TABLE images DROP FOREIGN KEY images_ibfk_1;

ALTER TABLE sensor_data MODIFY upload_id bigint;
ALTER TABLE images MODIFY upload_id bigint;
ALTER TABLE uploads MODIFY id bigint NOT NULL AUTO_INCREMENT;

#ALTER TABLE sensor_data ADD CONSTRAINT sensor_data_ibfk_1 FOREIGN KEY (upload_id) REFERENCES uploads (id);
#ALTER TABLE images ADD CONSTRAINT images_ibfk_1 FOREIGN KEY (upload_id) REFERENCES uploads (id);


# sensor_data.id

#ALTER TABLE el_calculations DROP FOREIGN KEY el_calculations_ibfk_2;
#ALTER TABLE el_calculations DROP FOREIGN KEY el_calculations_ibfk_3;

ALTER TABLE el_calculations MODIFY original_data bigint;
ALTER TABLE el_calculations MODIFY calculated_data bigint;
ALTER TABLE sensor_data MODIFY id bigint NOT NULL AUTO_INCREMENT;

#ALTER TABLE el_calculations ADD CONSTRAINT el_calculations_ibfk_2 FOREIGN KEY (original_data) REFERENCES sensor_data (id);
#ALTER TABLE el_calculations ADD CONSTRAINT el_calculations_ibfk_3 FOREIGN KEY (calculated_data) REFERENCES sensor_data (id);


# images.id

ALTER TABLE images MODIFY id bigint NOT NULL AUTO_INCREMENT;


# el_calculations.id

ALTER TABLE el_calculations MODIFY id bigint NOT NULL AUTO_INCREMENT;


