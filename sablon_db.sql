-- ============================================================
-- Database Rekap Sablon  (XAMPP / MariaDB)  -- versi dengan tambahan harga
-- Cara pakai: phpMyAdmin > tab Import > pilih file ini > Import
-- Aman diimpor berulang kali. Semua pesanan ikut terhapus,
-- tabel pelanggan tidak disentuh.
-- ============================================================

CREATE DATABASE IF NOT EXISTS sablon_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE sablon_db;

-- Hapus tabel yang akan dibuat ulang (anak dulu, induk belakangan)
DROP TABLE IF EXISTS pesanan_tambahan;
DROP TABLE IF EXISTS detail_pesanan;
DROP TABLE IF EXISTS pesanan;
DROP TABLE IF EXISTS tambahan;
DROP TABLE IF EXISTS harga_bahan;
DROP TABLE IF EXISTS bahan_kain;
DROP TABLE IF EXISTS jenis_sablon;
DROP TABLE IF EXISTS ukuran;

-- ------------------------------------------------------------
-- Tabel master
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pelanggan (
  id_pelanggan INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  no_hp VARCHAR(20)
);

-- tambahan_harga = tambahan per kaos untuk ukuran tersebut (0 = FREE)
CREATE TABLE ukuran (
  id_ukuran INT AUTO_INCREMENT PRIMARY KEY,
  nama_ukuran VARCHAR(10) NOT NULL,
  tambahan_harga INT NOT NULL DEFAULT 0
);

CREATE TABLE bahan_kain (
  id_bahan INT AUTO_INCREMENT PRIMARY KEY,
  nama_bahan VARCHAR(50) NOT NULL
);

-- Harga per pcs menurut bahan dan tier kuantitas
-- qty_max NULL = tanpa batas atas, harga NULL = CALL ADMIN (nego)
CREATE TABLE harga_bahan (
  id_harga INT AUTO_INCREMENT PRIMARY KEY,
  id_bahan INT NOT NULL,
  qty_min INT NOT NULL,
  qty_max INT NULL,
  harga INT NULL,
  FOREIGN KEY (id_bahan) REFERENCES bahan_kain(id_bahan)
);

-- Daftar tambahan harga (per kaos). harga 0 = FREE.
-- otomatis = 1 : dihitung otomatis dari jumlah warna, bukan pilihan kasir
CREATE TABLE tambahan (
  id_tambahan INT AUTO_INCREMENT PRIMARY KEY,
  kelompok VARCHAR(10) NOT NULL,            -- Bahan / Sablon
  nama VARCHAR(60) NOT NULL,
  harga INT NOT NULL DEFAULT 0,
  otomatis TINYINT NOT NULL DEFAULT 0
);

-- ------------------------------------------------------------
-- Tabel transaksi
-- ------------------------------------------------------------
CREATE TABLE pesanan (
  id_pesanan INT AUTO_INCREMENT PRIMARY KEY,
  id_pelanggan INT NOT NULL,
  tanggal DATE NOT NULL,
  finishing VARCHAR(10) NOT NULL,           -- Doff / Glossy / Kasar
  jumlah_warna TINYINT NOT NULL,            -- 4 warna pertama sudah termasuk
  FOREIGN KEY (id_pelanggan) REFERENCES pelanggan(id_pelanggan)
);

-- harga_satuan = harga final per kaos untuk baris ukuran ini
-- (harga dasar + tambahan ukuran + semua tambahan pesanan), snapshot saat transaksi
CREATE TABLE detail_pesanan (
  id_detail INT AUTO_INCREMENT PRIMARY KEY,
  id_pesanan INT NOT NULL,
  id_bahan INT NOT NULL,
  id_ukuran INT NOT NULL,
  jumlah INT NOT NULL,
  harga_satuan INT NOT NULL,
  FOREIGN KEY (id_pesanan) REFERENCES pesanan(id_pesanan),
  FOREIGN KEY (id_bahan) REFERENCES bahan_kain(id_bahan),
  FOREIGN KEY (id_ukuran) REFERENCES ukuran(id_ukuran)
);

-- Tambahan yang dipilih pada satu pesanan (harga = snapshot per kaos)
CREATE TABLE pesanan_tambahan (
  id_pesanan INT NOT NULL,
  id_tambahan INT NOT NULL,
  harga INT NOT NULL,
  PRIMARY KEY (id_pesanan, id_tambahan),
  FOREIGN KEY (id_pesanan) REFERENCES pesanan(id_pesanan),
  FOREIGN KEY (id_tambahan) REFERENCES tambahan(id_tambahan)
);

-- ------------------------------------------------------------
-- Data awal
-- ------------------------------------------------------------
INSERT INTO ukuran (nama_ukuran, tambahan_harga) VALUES
('XS', 0), ('S', 0), ('M', 0), ('L', 0), ('XL', 0),
('XXL', 3000), ('3XL', 3000),
('4XL', 7000), ('5XL', 7000);

INSERT INTO bahan_kain (nama_bahan) VALUES
('Cotton Combed 30s'),
('Cotton Combed 24s'),
('Cotton Combed 20s'),
('Cotton Combed 16s & Hevy');

INSERT INTO harga_bahan (id_bahan, qty_min, qty_max, harga) VALUES
(1, 12, 9999, 55000), (1, 121, 250, 53000), (1, 9999, NULL, NULL),
(2, 12, 9999, 60000), (2, 121, 250, 58000), (2, 9999, NULL, NULL),
(3, 12, 9999, 65000), (3, 121, 250, 63000), (3, 9999, NULL, NULL),
(4, 12, 9999, 75000), (4, 121, 250, 73000), (4, 9999, NULL, NULL);

-- Tambahan BAHAN (nomor 1-11) dan SABLON (nomor 12-23), lalu satu item otomatis (24)
INSERT INTO tambahan (kelompok, nama, harga, otomatis) VALUES
('Bahan',  'Oversize',                    7000, 0),
('Bahan',  'Lengan panjang',              5000, 0),
('Bahan',  'Rib/karet lengan',               0, 0),
('Bahan',  'Reglan pendek',               3000, 0),
('Bahan',  'Reglan 3/4',                  5000, 0),
('Bahan',  'Reglan panjang',              8000, 0),
('Bahan',  'Bahan kombinasi',             5000, 0),
('Bahan',  'Saku',                        5000, 0),
('Bahan',  'Kerah',                       5000, 0),
('Bahan',  'Manset',                      3000, 0),
('Bahan',  'Jahit label satin/woven',     5000, 0),
('Sablon', 'Desain ukuran A2',            4000, 0),
('Sablon', 'Raster hitam putih',             0, 0),
('Sablon', 'Raster warna & CMYK',         3000, 0),
('Sablon', 'Sablon silver',               5000, 0),
('Sablon', 'Sablon emas',                 5000, 0),
('Sablon', 'Sablon glow in the dark',     5000, 0),
('Sablon', 'Sablon plascharge',           8000, 0),
('Sablon', 'Sablon 3D/high density',     10000, 0),
('Sablon', 'Tag leher',                      0, 0),
('Sablon', 'Tag leher size',              2000, 0),
('Sablon', 'Fluorescente/stabilo',        5000, 0),
('Sablon', 'Sablon overprint',            1000, 0),
('Sablon', 'Tambah warna/screen (per 2 warna)', 1500, 1);
