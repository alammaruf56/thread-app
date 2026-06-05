-- যদি আগের কোনো টেবিল থেকে থাকে তবে তা ডিলিট করবে (যাতে এরর না আসে)
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS threads;

-- ১. সুতার ইনভেন্টরি টেবিল
CREATE TABLE threads (
    thread_code VARCHAR(100) PRIMARY KEY,
    thread_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT NULL,
    current_stock INT DEFAULT 0
);

-- ২. সেলার টেবিল
CREATE TABLE sellers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) DEFAULT NULL,
    address TEXT DEFAULT NULL
);

-- ৩. কাস্টমার টেবিল
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) DEFAULT NULL,
    address TEXT DEFAULT NULL
);

-- ৪. কেনা-বেচার ট্রানজেকশন টেবিল (যা সেলার ও কাস্টমারের সাথে সুতার কোড কানেক্ট করবে)
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- 'BUY' অথবা 'SELL'
    thread_code VARCHAR(100) NOT NULL,
    party_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (thread_code) REFERENCES threads(thread_code) ON UPDATE CASCADE
);