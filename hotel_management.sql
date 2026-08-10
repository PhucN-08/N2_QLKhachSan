CREATE DATABASE IF NOT EXISTS ql_khachsan;
USE ql_khachsan;

-- Bảng Rooms
CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type ENUM('Standard','Deluxe','Suite') NOT NULL,
    status ENUM('Empty','Booked','Occupied','Deactivated') DEFAULT 'Empty',
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255)
);

-- Bảng Customers
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    id_type ENUM('CCCD','Passport') DEFAULT 'CCCD',
    id_number VARCHAR(20) UNIQUE
);

-- Bảng Bookings
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    room_id INT NOT NULL,
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    actual_checkin DATETIME,
    actual_checkout DATETIME,
    status ENUM('Booked','Cancelled','CheckedIn','CheckedOut') DEFAULT 'Booked',
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    extended_hours INT DEFAULT 0,
    extra_fee DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Bảng Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Paid','Unpaid','Cancelled') DEFAULT 'Unpaid',
    payment_method ENUM('Cash','BankTransfer') DEFAULT 'Cash',
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
