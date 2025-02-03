-- Create the table to store the data
CREATE TABLE CarObservation (
    Timestamp BIGINT PRIMARY KEY,
    Car1_Location_X FLOAT,
    Car1_Location_Y INT,
    Car1_Location_Z FLOAT,
    Car2_Location_X FLOAT,
    Car2_Location_Y INT,
    Car2_Location_Z FLOAT,
    Occluded_Image_View VARCHAR(255),
    Occluding_Car_View VARCHAR(255),
    Ground_Truth_View VARCHAR(255),
    PedestrianLocationX_TopLeft INT,
    PedestrianLocationY_TopLeft INT,
    PedestrianLocationX_BottomRight INT,
    PedestrianLocationY_BottomRight INT
);
