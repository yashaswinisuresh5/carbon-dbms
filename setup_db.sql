CREATE DATABASE IF NOT EXISTS carbon_footprint_db;
USE carbon_footprint_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Activities Table (Stores predefined emission factors)
CREATE TABLE IF NOT EXISTS Activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    activity_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    emission_factor DECIMAL(10, 4) NOT NULL,
    description TEXT
);

-- 3. User_Activity Table (Logs individual user activities)
CREATE TABLE IF NOT EXISTS User_Activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    carbon_output DECIMAL(10, 4) NOT NULL,
    date DATE NOT NULL,
    notes VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES Activities(activity_id) ON DELETE CASCADE
);

-- Insert Default Activities (Emission Factors per unit)
-- Sources: EPA, DEFRA, etc. (Approximations for project)

-- Transport
INSERT INTO Activities (activity_name, category, unit, emission_factor, description) VALUES
('Petrol Car Driving', 'Transport', 'km', 0.1920, 'Average petrol car'),
('Diesel Car Driving', 'Transport', 'km', 0.1710, 'Average diesel car'),
('Electric Car Driving', 'Transport', 'km', 0.0530, 'Average electric vehicle'),
('Motorcycle', 'Transport', 'km', 0.1030, 'Average motorcycle'),
('Bus Journey', 'Transport', 'km', 0.1050, 'Average local bus'),
('Train Journey', 'Transport', 'km', 0.0410, 'National rail'),
('Domestic Flight', 'Transport', 'km', 0.2550, 'Short haul flights');

-- Electricity
INSERT INTO Activities (activity_name, category, unit, emission_factor, description) VALUES
('Grid Electricity', 'Electricity', 'kWh', 0.8500, 'Average grid electricity (India estimate)'),
('Solar Electricity', 'Electricity', 'kWh', 0.0410, 'Rooftop solar lifecycle emissions');

-- Food
INSERT INTO Activities (activity_name, category, unit, emission_factor, description) VALUES
('Beef Meal', 'Food', 'kg', 27.000, 'Beef consumption'),
('Chicken Meal', 'Food', 'kg', 6.9000, 'Chicken consumption'),
('Fish Meal', 'Food', 'kg', 5.2000, 'Farmed fish'),
('Vegetarian Meal', 'Food', 'kg', 2.0000, 'Average vegetarian diet'),
('Vegan Meal', 'Food', 'kg', 1.5000, 'Average vegan diet'),
('Rice', 'Food', 'kg', 4.0000, 'White rice production'),
('Milk', 'Food', 'liter', 3.0000, 'Cow milk');

-- Shopping / Goods
INSERT INTO Activities (activity_name, category, unit, emission_factor, description) VALUES
('Cotton T-Shirt', 'Shopping', 'item', 4.3000, 'New cotton shirt production'),
('Jeans', 'Shopping', 'item', 33.400, 'New denim jeans production'),
('Smartphone', 'Shopping', 'item', 55.000, 'New smartphone lifecycle'),
('Laptop', 'Shopping', 'item', 210.00, 'New laptop lifecycle');

-- Waste
INSERT INTO Activities (activity_name, category, unit, emission_factor, description) VALUES
('General Waste to Landfill', 'Waste', 'kg', 0.4500, 'Mixed municipal waste'),
('Recycled Waste', 'Waste', 'kg', 0.0200, 'Paper/Plastic recycled'),
('Composted Organic Waste', 'Waste', 'kg', 0.1500, 'Food/Garden waste composted');
