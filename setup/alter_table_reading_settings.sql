ALTER TABLE reading_settings DROP range_x0;
ALTER TABLE reading_settings DROP range_y0;
ALTER TABLE reading_settings DROP range_x1;
ALTER TABLE reading_settings DROP range_y1;

ALTER TABLE reading_settings ADD range_x INT;
ALTER TABLE reading_settings ADD range_y INT;
ALTER TABLE reading_settings ADD range_w INT;
ALTER TABLE reading_settings ADD range_h INT;
ALTER TABLE reading_settings ADD rotation_angle FLOAT;
ALTER TABLE reading_settings ADD num_rects INT;
ALTER TABLE reading_settings ADD max_brightness FLOAT;
ALTER TABLE reading_settings ADD min_brightness FLOAT;
ALTER TABLE reading_settings ADD max_contrast FLOAT;
ALTER TABLE reading_settings ADD min_contrast FLOAT;

