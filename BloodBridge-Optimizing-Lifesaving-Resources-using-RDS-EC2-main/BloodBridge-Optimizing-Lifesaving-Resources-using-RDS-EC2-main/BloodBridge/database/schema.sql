-- =====================================================
-- BloodBridge Database Schema
-- AWS RDS MySQL Compatible
-- Optimizing Lifesaving Resources
-- =====================================================

CREATE DATABASE IF NOT EXISTS bloodbridge_db;
USE bloodbridge_db;

-- =====================================================
-- Table: users (Admin, Hospital, Blood Bank Manager)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'hospital', 'bloodbank') NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: donors
-- =====================================================
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT,
    city VARCHAR(50),
    last_donation_date DATE,
    status ENUM('active', 'inactive', 'deferred') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: blood_requests
-- =====================================================
CREATE TABLE IF NOT EXISTS blood_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    quantity INT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    patient_name VARCHAR(100),
    reason TEXT,
    required_by_date DATE,
    status ENUM('pending', 'approved', 'fulfilled', 'rejected', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES users(id)
);

-- =====================================================
-- Table: inventory
-- =====================================================
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') UNIQUE NOT NULL,
    units INT DEFAULT 0,
    min_threshold INT DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: blood_drives
-- =====================================================
CREATE TABLE IF NOT EXISTS blood_drives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    city VARCHAR(50),
    date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    description TEXT,
    status ENUM('upcoming', 'ongoing', 'completed') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: donation_history
-- =====================================================
CREATE TABLE IF NOT EXISTS donation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    drive_id INT,
    donation_date DATE,
    scheduled_date DATE,
    units INT DEFAULT 1,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(id),
    FOREIGN KEY (drive_id) REFERENCES blood_drives(id)
);

-- =====================================================
-- Insert Sample Data
-- =====================================================

-- Admin User (Demo Credentials)
INSERT INTO users (name, email, password, role, phone, city, status) VALUES
('System Administrator', 'admin@bloodbridge.com', 
 'admin123', 
 'admin', '+1-555-0100', 'New York', 'active');

-- Note: The hashed password above is for 'admin123' using werkzeug generate_password_hash
-- For direct SQL insertion, use: 
-- Password hash for 'admin123': pbkdf2:sha256:600000$...

-- Hospital Users
INSERT INTO users (name, email, password, role, phone, address, city, status) VALUES
('City General Hospital', 'citygen@hospital.com', 
 'admin123', 
 'hospital', '+1-555-0200', '123 Health Ave', 'New York', 'active'),

('St. Mary Medical Center', 'stmary@hospital.com', 
 'admin123', 
 'hospital', '+1-555-0300', '456 Care Blvd', 'Los Angeles', 'active'),

('Metro Emergency Hospital', 'metro@hospital.com', 
 'admin123', 
 'hospital', '+1-555-0400', '789 Emergency St', 'Chicago', 'active');

-- Blood Bank Manager
INSERT INTO users (name, email, password, role, phone, city, status) VALUES
('Central Blood Bank', 'central@bloodbank.com', 
 'admin123', 
 'bloodbank', '+1-555-0500', 'New York', 'active');

-- Donors
INSERT INTO donors (name, email, password, phone, blood_group, age, gender, address, city, last_donation_date, status) VALUES
('John Smith', 'john@email.com', 
 'admin123', 
 '+1-555-1001', 'O+', 28, 'Male', '101 Oak St', 'New York', '2024-01-15', 'active'),

('Sarah Johnson', 'sarah@email.com', 
 'admin123', 
 '+1-555-1002', 'A+', 32, 'Female', '202 Pine Ave', 'Los Angeles', '2024-02-20', 'active'),

('Michael Chen', 'michael@email.com', 
 'admin123', 
 '+1-555-1003', 'B+', 25, 'Male', '303 Maple Dr', 'Chicago', NULL, 'active'),

('Emily Davis', 'emily@email.com', 
 'admin123', 
 '+1-555-1004', 'AB-', 29, 'Female', '404 Birch Ln', 'New York', '2023-12-10', 'active'),

('Robert Wilson', 'robert@email.com', 
 'admin123', 
 '+1-555-1005', 'O-', 35, 'Male', '505 Cedar Rd', 'Los Angeles', '2024-03-01', 'active'),

('Lisa Anderson', 'lisa@email.com', 
 'admin123', 
 '+1-555-1006', 'A-', 27, 'Female', '606 Elm St', 'Chicago', NULL, 'active'),

('David Brown', 'david@email.com', 
 'admin123', 
 '+1-555-1007', 'B-', 31, 'Male', '707 Spruce Way', 'New York', '2024-01-28', 'active'),

('Jennifer Martinez', 'jennifer@email.com', 
 'admin123', 
 '+1-555-1008', 'AB+', 24, 'Female', '808 Willow Ct', 'Los Angeles', NULL, 'active');

-- Inventory
INSERT INTO inventory (blood_group, units, min_threshold) VALUES
('A+', 45, 10),
('A-', 22, 10),
('B+', 38, 10),
('B-', 15, 10),
('AB+', 12, 10),
('AB-', 8, 10),
('O+', 52, 10),
('O-', 18, 10);

-- Blood Drives
INSERT INTO blood_drives (title, location, city, date, start_time, end_time, description, status) VALUES
('Spring Blood Drive 2024', 'City Community Center', 'New York', '2024-04-15', '09:00:00', '17:00:00', 
 'Join us for our annual spring blood drive. Every donation saves up to 3 lives!', 'upcoming'),

('University Campus Drive', 'State University Hall', 'Los Angeles', '2024-04-20', '10:00:00', '16:00:00', 
 'Student and faculty blood donation event. Free health screening included.', 'upcoming'),

('Corporate Wellness Day', 'Tech Plaza Auditorium', 'Chicago', '2024-04-25', '08:00:00', '14:00:00', 
 'Corporate blood donation drive with refreshments and certificates.', 'upcoming'),

('Summer Lifesaver Campaign', 'Metro Park Pavilion', 'New York', '2024-05-10', '09:00:00', '18:00:00', 
 'Summer campaign to boost blood reserves for emergency season.', 'upcoming');

-- Blood Requests
INSERT INTO blood_requests (hospital_id, blood_group, quantity, priority, patient_name, reason, required_by_date, status) VALUES
(2, 'O-', 3, 'critical', 'Patient #1042', 'Emergency surgery - trauma victim', '2024-04-10', 'pending'),
(3, 'A+', 5, 'high', 'Patient #2081', 'Cancer treatment transfusion', '2024-04-12', 'pending'),
(2, 'B+', 2, 'medium', 'Patient #1567', 'Scheduled cardiac surgery', '2024-04-15', 'approved'),
(4, 'AB-', 1, 'critical', 'Patient #3092', 'Neonatal emergency', '2024-04-08', 'fulfilled'),
(3, 'O+', 4, 'high', 'Patient #2156', 'Accident victim - multiple injuries', '2024-04-11', 'pending'),
(2, 'A-', 2, 'medium', 'Patient #1789', 'Anemia treatment', '2024-04-14', 'approved');

-- Donation History
INSERT INTO donation_history (donor_id, drive_id, donation_date, units, status, notes) VALUES
(1, 1, '2024-01-15', 1, 'completed', 'Regular donation - no issues'),
(2, 2, '2024-02-20', 1, 'completed', 'First time donor - excellent experience'),
(4, 1, '2023-12-10', 1, 'completed', 'Holiday season donation'),
(5, 3, '2024-03-01', 1, 'completed', 'Corporate drive participant');

-- =====================================================
-- Views for Dashboard Analytics
-- =====================================================

CREATE VIEW IF NOT EXISTS vw_inventory_status AS
SELECT 
    blood_group,
    units,
    min_threshold,
    CASE 
        WHEN units < min_threshold THEN 'CRITICAL'
        WHEN units < min_threshold * 2 THEN 'LOW'
        ELSE 'NORMAL'
    END as stock_status
FROM inventory;

CREATE VIEW IF NOT EXISTS vw_donor_eligibility AS
SELECT 
    id,
    name,
    blood_group,
    last_donation_date,
    DATEDIFF(CURDATE(), last_donation_date) as days_since_donation,
    CASE 
        WHEN last_donation_date IS NULL THEN 'ELIGIBLE'
        WHEN DATEDIFF(CURDATE(), last_donation_date) >= 56 THEN 'ELIGIBLE'
        ELSE 'NOT ELIGIBLE'
    END as eligibility_status
FROM donors;

-- =====================================================
-- End of Schema
-- =====================================================
