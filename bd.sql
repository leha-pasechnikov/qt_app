CREATE DATABASE exam;
USE exam;

CREATE TABLE user (
    id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    date_save DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

INSERT INTO user (id, username, password) VALUES (1, 'admin', 'admin');

INSERT INTO products (id, name, date_save, price) VALUES
(1, 'свекла', '2025-06-24', 40.00),
(2, 'яблоки', '2025-06-25', 120.00),
(3, 'картофель', '2025-06-21', 65.00),
(4, 'огурцы', '2025-06-26', 80.00),
(5, 'персики', '2025-06-24', 250.00);
