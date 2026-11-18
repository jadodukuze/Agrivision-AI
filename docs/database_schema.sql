-- AgriVision AI MySQL reference schema.
-- Keep these column types aligned with backend/app/models.py.
CREATE DATABASE IF NOT EXISTS agrivision_ai
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE agrivision_ai;

CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'farmer',
  preferred_language VARCHAR(5) NOT NULL DEFAULT 'en',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  KEY ix_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crop_cases (
  id INT NOT NULL AUTO_INCREMENT,
  farmer_id INT NOT NULL,
  crop_name VARCHAR(80) NOT NULL,
  location VARCHAR(120) NULL,
  description TEXT NULL,
  image_path VARCHAR(255) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'submitted',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_crop_cases_farmer_id (farmer_id),
  KEY ix_crop_cases_status (status),
  CONSTRAINT fk_crop_cases_farmer
    FOREIGN KEY (farmer_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS expert_reviews (
  id INT NOT NULL AUTO_INCREMENT,
  case_id INT NOT NULL,
  expert_id INT NOT NULL,
  assessment TEXT NOT NULL,
  recommended_next_steps TEXT NULL,
  reviewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_expert_reviews_case_id (case_id),
  KEY ix_expert_reviews_expert_id (expert_id),
  CONSTRAINT fk_expert_reviews_case
    FOREIGN KEY (case_id) REFERENCES crop_cases(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_expert_reviews_expert
    FOREIGN KEY (expert_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reserved for a future, separately evaluated AI model integration.
-- The current application does not create or expose AI predictions.
CREATE TABLE IF NOT EXISTS ai_predictions (
  id INT NOT NULL AUTO_INCREMENT,
  case_id INT NOT NULL,
  model_version VARCHAR(80) NOT NULL,
  predicted_label VARCHAR(120) NOT NULL,
  confidence DECIMAL(6,5) NULL,
  reviewed_by_expert BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_ai_predictions_case_id (case_id),
  CONSTRAINT fk_ai_predictions_case
    FOREIGN KEY (case_id) REFERENCES crop_cases(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
