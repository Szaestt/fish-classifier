-- ============================================================
-- Fish Classifier - Database Schema
-- Untuk XAMPP (MySQL/MariaDB) via phpMyAdmin
--
-- Cara pakai:
--   1. Start Apache + MySQL di XAMPP Control Panel
--   2. Buka http://localhost/phpmyadmin
--   3. Tab "Import" -> pilih file ini -> Go
--      (database dibuat otomatis, tidak perlu bikin manual)
-- ============================================================

CREATE DATABASE IF NOT EXISTS `fish_classifier`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `fish_classifier`;

-- ------------------------------------------------------------
-- Tabel users: akun login (password disimpan sebagai bcrypt hash)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(50)  NOT NULL,
  `email`         VARCHAR(100) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at`    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_username` (`username`),
  UNIQUE KEY `uq_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Tabel predictions: riwayat setiap prediksi gambar
-- user_id boleh NULL = prediksi tanpa login (guest)
-- top_k disimpan sebagai JSON string, contoh:
--   [{"class":"Tuna","confidence":0.93}, ...]
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `predictions` (
  `id`              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  `user_id`         INT UNSIGNED  DEFAULT NULL,
  `image_name`      VARCHAR(255)  NOT NULL,
  `predicted_class` VARCHAR(50)   NOT NULL,
  `confidence`      DECIMAL(6,5)  NOT NULL,
  `top_k`           TEXT          DEFAULT NULL,
  `model_name`      VARCHAR(30)   NOT NULL DEFAULT 'cnn_scratch',
  `input_size`      SMALLINT UNSIGNED NOT NULL DEFAULT 160,
  `elapsed_ms`      INT UNSIGNED  NOT NULL DEFAULT 0,
  `created_at`      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_predictions_user` (`user_id`),
  KEY `idx_predictions_class` (`predicted_class`),
  KEY `idx_predictions_created` (`created_at`),
  CONSTRAINT `fk_predictions_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- (Opsional) Contoh data buat testing tampilan riwayat.
-- Hapus bagian ini kalau mau mulai dari kosong.
-- ------------------------------------------------------------
INSERT INTO `predictions`
  (`user_id`, `image_name`, `predicted_class`, `confidence`, `top_k`, `model_name`, `input_size`, `elapsed_ms`)
VALUES
  (NULL, 'contoh_tuna.jpg', 'Tuna', 0.93215,
   '[{"class":"Tuna","confidence":0.93215},{"class":"Tongkol","confidence":0.05121},{"class":"Nila","confidence":0.01043}]',
   'cnn_scratch', 160, 6812),
  (NULL, 'contoh_nila.jpg', 'Nila', 0.88410,
   '[{"class":"Nila","confidence":0.8841},{"class":"Bawal Putih","confidence":0.07332},{"class":"Pari","confidence":0.02514}]',
   'cnn_scratch', 160, 7104);
