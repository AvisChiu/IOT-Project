-- --------------------------------------------------------
-- 主機:                           127.0.0.1
-- 伺服器版本:                        10.3.14-MariaDB - mariadb.org binary distribution
-- 伺服器操作系統:                      Win64
-- HeidiSQL 版本:                  9.5.0.5196
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- 傾印 iot 的資料庫結構
CREATE DATABASE IF NOT EXISTS `iot` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `iot`;

-- 傾印  表格 iot.device 結構
CREATE TABLE IF NOT EXISTS `device` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT '0',
  `level` smallint(5) unsigned NOT NULL DEFAULT 4,
  PRIMARY KEY (`id`),
  KEY `uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 取消選取資料匯出。
-- 傾印  表格 iot.th 結構
CREATE TABLE IF NOT EXISTS `th` (
  `Time` datetime NOT NULL,
  `UUID` varchar(50) NOT NULL,
  `Temperature` float DEFAULT NULL,
  `Humidity` float DEFAULT NULL,
  PRIMARY KEY (`Time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 取消選取資料匯出。
-- 傾印  表格 iot.users 結構
CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(64) NOT NULL,
  `password` varchar(256) NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `level` smallint(5) unsigned DEFAULT 5,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

-- 取消選取資料匯出。
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
