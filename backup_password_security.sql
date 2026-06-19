-- MySQL dump 10.13  Distrib 9.3.0, for macos15.2 (arm64)
--
-- Host: 127.0.0.1    Database: password_security
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `details` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
INSERT INTO `activity_logs` VALUES (1,1,'REGISTER','Đăng ký thành công với username=nguyenvana, strength=Strong','2026-06-13 01:10:00','10.0.0.1'),(2,1,'LOGIN_SUCCESS','Đăng nhập thành công (username=nguyenvana)','2026-06-13 01:10:00','10.0.0.1'),(3,1,'UPDATE_PROFILE','Cập nhật: phone','2026-06-13 01:10:00','10.0.0.1'),(4,2,'REGISTER','Đăng ký thành công với username=tranthib, strength=Strong','2026-06-13 01:10:00','192.168.1.5'),(5,2,'LOGIN_SUCCESS','Đăng nhập thành công (username=tranthib)','2026-06-13 01:10:00','192.168.1.5'),(6,3,'REGISTER','Đăng ký thành công với username=levanc, strength=Strong','2026-06-13 01:10:00','10.0.0.3'),(7,3,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-13 01:10:00','203.0.113.45'),(8,3,'LOGIN_FAILED','Sai mật khẩu. Lần thử 2/5','2026-06-13 01:10:00','203.0.113.45'),(9,3,'LOGIN_FAILED','Sai mật khẩu. Lần thử 3/5','2026-06-13 01:10:00','198.51.100.23'),(10,3,'LOGIN_FAILED','Sai mật khẩu. Lần thử 4/5','2026-06-13 01:10:00','198.51.100.23'),(11,3,'LOGIN_FAILED','Sai mật khẩu. Lần thử 5/5','2026-06-13 01:10:00','192.0.2.99'),(12,3,'LOGIN_LOCKED','Tài khoản bị khóa 3 phút do nhập sai 5 lần','2026-06-13 01:10:00','192.0.2.99'),(13,4,'REGISTER','Đăng ký thành công với username=phamthid, strength=Strong','2026-06-13 01:10:00','10.0.0.4'),(14,4,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-13 01:10:00','10.0.0.4'),(15,4,'LOGIN_FAILED','Sai mật khẩu. Lần thử 2/5','2026-06-13 01:10:00','10.0.0.4'),(16,4,'LOGIN_FAILED','Sai mật khẩu. Lần thử 3/5','2026-06-13 01:10:00','10.0.0.4'),(17,5,'REGISTER','Đăng ký thành công với username=hoangvane, strength=Strong','2026-06-13 01:10:00','10.0.0.2'),(18,5,'LOGIN_SUCCESS','Đăng nhập thành công (username=hoangvane)','2026-06-13 01:10:00','10.0.0.2'),(19,5,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-13 01:10:00','10.0.0.2'),(20,6,'REGISTER','Đăng ký thành công với username=vuthif, strength=Strong','2026-06-13 01:10:00','172.16.0.10'),(21,6,'LOGIN_SUCCESS','Đăng nhập thành công (username=vuthif)','2026-06-13 01:10:00','172.16.0.10'),(22,7,'REGISTER','Đăng ký thành công với username=minhthu11, strength=Medium','2026-06-13 02:26:57','192.168.0.104'),(23,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:27:21','192.168.0.104'),(24,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:32:00','192.168.0.104'),(25,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:44:21','192.168.0.104'),(26,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:51:22','192.0.2.99'),(27,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:54:51','192.168.0.104'),(28,7,'UPDATE_PROFILE','Cập nhật: phone','2026-06-13 02:55:19','203.0.113.45'),(29,7,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-13 02:55:45','192.168.0.104'),(30,7,'LOGOUT','Người dùng đăng xuất','2026-06-13 02:56:05','203.0.113.45'),(31,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-13 02:56:22','192.168.0.104'),(32,7,'LOGOUT','Người dùng đăng xuất','2026-06-13 02:56:31','198.51.100.23'),(33,8,'REGISTER','Đăng ký thành công với username=nhunguyen, strength=Medium','2026-06-13 03:19:23','192.168.0.104'),(34,8,'LOGIN_SUCCESS','Đăng nhập thành công (username=nhunguyen)','2026-06-13 03:19:39','192.168.0.104'),(35,8,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-13 03:20:02','203.0.113.45'),(36,8,'LOGOUT','Người dùng đăng xuất','2026-06-13 03:20:11','203.0.113.177'),(37,9,'REGISTER','Đăng ký thành công với username=nhunho, strength=Medium','2026-06-13 17:46:07','203.0.113.177'),(38,10,'REGISTER','Đăng ký thành công với username=nghioilanghi, strength=Strong','2026-06-13 18:08:39','192.168.0.236'),(39,4,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-13 19:43:28','192.168.0.236'),(40,11,'REGISTER','Đăng ký thành công với username=tramthuy, strength=Strong','2026-06-14 08:19:16','192.168.0.236'),(41,11,'LOGIN_SUCCESS','Đăng nhập thành công (username=tramthuy)','2026-06-14 08:19:36','192.168.0.236'),(42,11,'LOGIN_SUCCESS','Đăng nhập thành công (username=tramthuy)','2026-06-14 08:25:03','10.23.109.8'),(43,11,'LOGIN_SUCCESS','Đăng nhập thành công (username=tramthuy)','2026-06-14 08:26:26','198.51.100.23'),(44,11,'UPDATE_PROFILE','Cập nhật: full_name','2026-06-14 08:26:55','192.168.0.236'),(45,11,'UPDATE_PROFILE','Cập nhật: full_name, phone','2026-06-14 08:27:15','10.140.139.205'),(46,11,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-14 08:27:44','192.168.0.236'),(47,11,'LOGOUT','Người dùng đăng xuất','2026-06-14 08:27:55','192.168.0.236'),(48,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-17 05:13:03','192.168.0.236'),(49,7,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-17 05:17:43','192.168.0.236'),(50,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-17 05:34:41','192.168.0.236'),(51,7,'LOGOUT','Người dùng đăng xuất','2026-06-17 05:34:44','192.168.0.236'),(52,12,'REGISTER','Đăng ký thành công với username=bichtramtran, strength=Strong','2026-06-17 08:37:18','192.168.0.236'),(53,12,'LOGIN_SUCCESS','Đăng nhập thành công (username=bichtramtran)','2026-06-17 08:51:38','192.168.0.236'),(54,12,'UPDATE_PROFILE','Cập nhật: address','2026-06-17 08:52:43','198.51.100.23'),(55,12,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-17 08:53:35','192.168.0.236'),(56,12,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-17 08:55:39','192.168.0.236'),(57,12,'LOGOUT','Người dùng đăng xuất (Streamlit)','2026-06-17 08:55:42','192.168.0.236'),(58,12,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-18 09:24:11','10.218.143.133'),(59,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-18 09:24:29','198.51.100.23'),(60,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-18 12:40:20','192.168.0.236'),(61,7,'CHANGE_PASSWORD','Thay đổi mật khẩu thành công','2026-06-18 12:40:56','192.168.0.236'),(62,7,'LOGOUT','Người dùng đăng xuất','2026-06-18 12:43:41','172.16.122.17'),(63,7,'LOGIN_SUCCESS','Đăng nhập thành công (username=minhthu11)','2026-06-18 18:01:26','192.168.10.124'),(64,7,'UPDATE_PROFILE','Cập nhật: identify_card, address','2026-06-18 18:02:42','10.123.23.170'),(65,7,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-19 00:16:29','10.140.58.242'),(66,11,'LOGIN_FAILED','Sai mật khẩu. Lần thử 1/5','2026-06-19 00:16:29','10.140.58.242');
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` text NOT NULL,
  `full_name` text,
  `email` text,
  `phone` text,
  `identify_card` text,
  `address` text,
  `failed_login_attempts` int DEFAULT '0',
  `locked_until` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'nguyenvana','$argon2id$v=19$m=102400,t=2,p=8$TwCtAaHEwmUuPc9QXfnMpg$QIZv8m8bC2pxUGu3OzMo5Kb3abCeRlsWcPeyDslD9DE','Uvc+IxGt4Xr5KfUydCUIdsrimiVCkJ8Nx+q7EMpIhUfVcbScJZKpCsIhSw==','ru3u8PstHU/J7x+ogd22OvDzDXSyL4ifQzohmdFKnN6TUZwb31NRyrYsR8Xa6kGj','GsLe2bbGxAeRzqzA2b8gknU8PGyjhtW5D15O+9PVDZTaRVxwOqI=','1dx0uvxYY13nYIX8r6qEqyrwlmcY69Y0sqRXOkFh3MrKzbXBKw/7rg==','CT8v8oS3JGEDEo55rVwnqwJt3W4iHUTLJZSBR5vZO6msdBFg2mTv5EAXg/76BQjePAX7/fUnHnRTw+4=',0,NULL),(2,'tranthib','$argon2id$v=19$m=102400,t=2,p=8$b2L66KRL+as557nL6UDEEg$WgG8HN4G0WbMn8jcVxc9+2rpoQimHMDTy4gjzt69OkY','D0cOKsr0noai4X7mcoXNDlNCMGQmz7NoVSpjeixJSAzoWPil4R8RHS9X','zqUsDTNdUOTF1oxKZmqi+8VOD8mt7pPic6ZT/vmdWrLBZI8d0RR6H+iWByUgzw==','tAiLviquIZX9OUn6X8Kp8jAxIy3ik08ElxGYXCvDDcro+4oXa7g=',NULL,NULL,0,NULL),(3,'levanc','$argon2id$v=19$m=102400,t=2,p=8$LEP0bpEFg+ZYnI5teS6LBQ$e5LAjtiCHFfDyKD+irGkuKSmZSyJSQdON/f+AwDdpsM','Wp+Rqp52kNYZIRWWRI/y/nWTM7c9PsiZE7wCkCx6RzLtdvDzNt8=','FtZBUM5BmNlU9i4JhJIUEpmH1JvgoTJiqMi6+VrLpQru+6CMzeFzb89ikXFxBA==','A+SLVTXIydxAc+FXcgjuwH17Evs0VFAb35nVBvK+Xz8/Em9UkGI=','GGmCgF+c+upGmOdmFBRRrkQFyULpfb0b7PyHE+2G2wIs9DqsqDs1tg==','lNpZCN1WYmQpYD/f+2f9f+XXV0io26ewvnd9/l679SVzlez+CJ9+SAHx6iMX4LuVTNZzteY=',5,'2026-06-13 08:13:00'),(4,'phamthid','$argon2id$v=19$m=102400,t=2,p=8$YUOiO20VeulYdT0/lTSQyA$hrZAOJLL/9xW8efBe+kXkIPP6TQyyHqEHdCtEobOefU','ZzjJ/Pxdxco9IrXj5gzCXLQQpSqWg1NaErYuHtKnb7Wi/meyuSEa3ZeO','RObeCYnlM6+sPyCanm/+MYMOV6sG4yP2vxppC4ufRCxrSWGHQBS7rAOD6eRmVw==','TeA5cCduP5QhM3dZHSIbJzXD3/RbLHyTeRGlCOmQaAEevTFgelU=','u07Qm+6WacC0ycwX8/fth3P4CcSEw4JGFC0tKCvJSZx3hFk7E1keFQ==',NULL,1,NULL),(5,'hoangvane','$argon2id$v=19$m=102400,t=2,p=8$68PCui0pB1o0IL5gdrdahA$dfXyG2n9Z3pPdPaRHXJ5mrIVO3bRr1KWRK2XSVYwEE8','d9eeVVbBf/YZAjSfa1TlWM5ekhqSr+CBp0tGuVxbD49uaQQN6SRU1lc=','TidENyx5Qf+RKbXtSnF/dFmI8d/vKGp4/10khC7DH0YxpSz2bkcyXUD06jJnz6JB','0UPr+O9LtFB6x0cXyOPSDX7XX+ZZ4fSkSg3UZZDF4GTJ/iGekmU=','XlQ1AjCRJj23Z8Qx8kmKQZs7fNP25+FTRVFKFPiKkiXyV1dKkNxmtA==','/gK9EezENP4no7clXcUTVzucX9gPqJXNnwkB2X1hcHP5+kM7RqMNtt6B1g3rbLRL2gXT52mbcidZZS3H4Qqra5e2mrt1fKhj',0,NULL),(6,'vuthif','$argon2id$v=19$m=102400,t=2,p=8$R6dYc98xAJ4aIplz0Nyaug$B1fdxQcacZnZM7xWfhNUfRoM5vflsf289KVZAuKn38I','kfxVnF/V8Rid/5T5Lx0n0jsSaRXZgSiMmBViO7uWd92ASQN+nn3W','2oTJEYgCRg1Tef6h/fzuXRJaNvBL36eDiq0Yfo3vf7wgdAvLPVGYdDFFY6iM28DPMksEzmk=',NULL,NULL,NULL,0,NULL),(7,'minhthu11','$argon2id$v=19$m=102400,t=2,p=8$R7Frn6rDvav3tiVzJz7LHw$oaQzcLzDfNt6ffPRjqRgt/sdRrz3oDYun+rRw3Uc1W8','w8rx3mmlvxAOpHG3+dHjG1PsV5usinF/3YDOliV/h5bOcrxH','YBgUzCvugDEICqZr8Qp80lhverc23oZNQRhxHnt7VWkF3nT+W4d6mBc=','R+d0LBI1zY+EnohX5l7ZQX07MFPdw7qFj+GPAvuIBm/Id5HS/iM=','tDePGptBO87cf9HkrxX8M9xrRIO4gF7bfR8gvBhY+MMkhuTJj17qyw==','M6A9gGloE3budRwD6phCUSFhfDU9JAOP7Gh5qIthD8YyCHBEhO/SF6+BxXHl4IJT/A==',1,NULL),(8,'nhunguyen','$argon2id$v=19$m=102400,t=2,p=8$Er7l/HYmM8Uwn6ar+F3rGw$hnbCrd81WX3CM0xIzHmJSqfDL89NygRtwi9N/+cqaPk','lcT8qBVbt7KGD3MLEbGLjtvDtdkEYWjK66OOLwmGVg==','tv0k7yUQl71jXo2/AmLUTM8135XyMOZ6x/jzz1WzwEuedYP9Ec4qqbc=',NULL,NULL,NULL,0,NULL),(9,'nhunho','$argon2id$v=19$m=102400,t=2,p=8$KtC1IGDC95/iB/pfTegL8g$2+BkfeaN/zBTnrz5bmgfQOHhNB8aE/Yp2tYfOOuPO2k','jZwUjSwekoUxwA4vaTCy0I2DZTmVqnC53hJIpwphN95P9Jm18Dg=','Ii5xLXobhR3nSUhq5PQLkkeCEWfMOI4aee2MU08Tb+hW4nchalVhm+0Ng/uu',NULL,NULL,NULL,0,NULL),(10,'nghioilanghi','$argon2id$v=19$m=102400,t=2,p=8$rRjd1lcdkqqdzgnz5ikNwQ$ZNqpClXoSk1jCY4tD5CDCZ1arnJCGC6GzTkAPfdu0nA','px/Lo454A7uBcmIKXcGq4qE85eV2mYJZUHqCBWgUQ+4=','Ve4hH5B2xqoBTH76+dGL7r3QKMvnhAGS8vYXLiRpFa8UmTKr3MDzFy8S',NULL,NULL,NULL,0,NULL),(11,'tramthuy','$argon2id$v=19$m=102400,t=2,p=8$AF2Lo7HKOmNy1kobrCy1tg$t/dShRsP5ja0keFoijycw1ABtmoT1N0M6fmZJ26H8dY','4ns6USymzUetWN2FW2NOR+xhZs32TvZGxXUKeOss24vdF12t6w==','ZmASS5plzlaOg6aTGgacdOpV1HOfruytXL8I8CSB9BXCMypgy2abyGOu','s1kJJYmBxlrKt4K2a5QWYjwRE3OzoCGybxdpnX9QoS3sEegok8M=',NULL,NULL,1,NULL),(12,'bichtramtran','$argon2id$v=19$m=102400,t=2,p=8$8vdgC2Qf0USdmtVXwFg9Hw$tl/VAL2edyVVoplf0XCW7pVIf3qg32lljTP7L+TDX1M','5V83E/tXjQ183qgx72Mu/Gi7AmC94pu+5mndjFo+kc0+qfojfyK5SqBy2NigVQ==','CcyseKyJU26EOyot0KD2/HAdIYu5jq3RFwmapdNEICk6wQ2OQp68wxyGpQ==','DZqv8ZVGL8arsqeBNDVdmjkbM5GbFhRugG7qXBz6TLwx4uVCRpQ=',NULL,'s9/zJdAlJW2nThIkhTFRBCmp21EZgZhzCkAFX5cwiS1M',1,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'password_security'
--
