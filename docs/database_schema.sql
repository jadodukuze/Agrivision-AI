-- AgriVision AI schema reference.
-- Keep this schema aligned with backend/app/models.py.
CREATE DATABASE IF NOT EXISTS agrivision_ai
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agrivision_ai;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'farmer',
  preferred_language VARCHAR(5) NOT NULL DEFAULT 'en',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_users_role (role)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS crop_cases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  farmer_id INT NOT NULL,
  crop_name VARCHAR(80) NOT NULL,
  location VARCHAR(120) NULL,
  description TEXT NULL,
  image_path VARCHAR(255) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'submitted',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cases_farmer_created (farmer_id, created_at),
  INDEX idx_cases_status (status),
  CONSTRAINT fk_cases_farmer
    FOREIGN KEY (farmer_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expert_reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  case_id INT NOT NULL,
  expert_id INT NOT NULL,
  assessment TEXT NOT NULL,
  recommended_next_steps TEXT NULL,
  reviewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_reviews_case (case_id),
  CONSTRAINT fk_reviews_case
    FOREIGN KEY (case_id) REFERENCES crop_cases(id),
  CONSTRAINT fk_reviews_expert
    FOREIGN KEY (expert_id) REFERENCES users(id)
) ENGINE=InnoDB;
