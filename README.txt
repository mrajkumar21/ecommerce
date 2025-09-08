# 🛒 E-commerce Database Management System

This project is a simple **E-commerce Management System** built with:

- **Python** (Streamlit for UI, SQLAlchemy for ORM, Pandas for reports)
- **MySQL** (database backend)

It provides features to:
- Manage products (add, update, delete)
- Place customer orders
- Update stock
- Generate order reports (CSV/Excel)

## ⚙️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/ecommerce-db.git
cd ecommerce-db
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```
1. create requirements.txt
2. Add below libraries
streamlit
sqlalchemy
pymysql
python-dotenv
pandas
openpyxl
cryptography
3. pip install -r requirements.txt

### 4. Create DataBase
```
CREATE DATABASE ecommerce_db 
USE ecommerce_db;
```
### 5. Create Tables
```
-- products table
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  stock INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- orders table
CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_name VARCHAR(255),
  customer_email VARCHAR(255),
  total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  status VARCHAR(32) NOT NULL DEFAULT 'PLACED',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- order_items table
CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  qty INT NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL,
  line_total DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- sample products
INSERT INTO products (name, description, price, stock) VALUES
('Note Book','Stationary',199.00,50),
('Mobile Phone','Electronics',3999.00,20),
('Laptop','Electronics',14999.50,100);

```

### 5. To Run the Application
python -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
