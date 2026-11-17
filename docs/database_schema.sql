-- AgriVision AI initial MySQL schema (review before production deployment).
CREATE DATABASE IF NOT EXISTS agrivision_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agrivision_ai;
CREATE TABLE IF NOT EXISTS users (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 full_name VARCHAR(120) NOT NULL,
 email VARCHAR(190) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role ENUM('farmer','expert','admin') NOT NULL DEFAULT 'farmer',
 preferred_language ENUM('en','rw') NOT NULL DEFAULT 'en',
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS crop_cases (
 id CHAR(36) PRIMARY KEY,
 farmer_id BIGINT UNSIGNED NOT NULL,
 crop_name VARCHAR(80) NOT NULL,
 location VARCHAR(120) NULL,
 description TEXT NULL,
 image_path VARCHAR(255) NOT NULL,
 status ENUM('submitted','under_review','reviewed','closed') NOT NULL DEFAULT 'submitted',
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_cases_farmer FOREIGN KEY (farmer_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS expert_reviews (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 case_id CHAR(36) NOT NULL,
 expert_id BIGINT UNSIGNED NOT NULL,
 assessment TEXT NOT NULL,
 recommended_next_steps TEXT NULL,
 reviewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_reviews_case FOREIGN KEY (case_id) REFERENCES crop_cases(id),
 CONSTRAINT fk_reviews_expert FOREIGN KEY (expert_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS ai_predictions (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 case_id CHAR(36) NOT NULL,
 model_version VARCHAR(80) NOT NULL,
 predicted_label VARCHAR(120) NOT NULL,
 confidence DECIMAL(6,5) NULL,
 reviewed_by_expert BOOLEAN NOT NULL DEFAULT FALSE,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_predictions_case FOREIGN KEY (case_id) REFERENCES crop_cases(id)
);
