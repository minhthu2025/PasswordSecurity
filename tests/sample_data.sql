-- ================================================================
-- sample_data.sql — Dữ liệu mẫu demo PasswordSecurity
-- PII đã mã hóa AES-256-GCM | Password đã hash Argon2id
--
-- Tài khoản mẫu (để đăng nhập khi demo):
--   username=nguyenvana      password=MyP@ssw0rd2026!      | Tài khoản bình thường, đầy đủ thông tin
--   username=tranthib        password=Secure#Hash99XY      | Tài khoản thiếu CMND và địa chỉ
--   username=levanc          password=Dragon$Fly2026#      | Tài khoản đang bị KHÓA — demo lockout
--   username=phamthid        password=CorrectH0rse!99      | Tài khoản đã nhập sai 3/5 lần — demo đếm failed attempts
--   username=hoangvane       password=Admin@Secure123!     | Tài khoản dùng để demo đổi mật khẩu
--   username=vuthif          password=Bl@ckP4nther_99!     | Tài khoản sinh viên, không có phone/CMND/address
-- ================================================================

-- Xóa data cũ (chỉ dùng khi reset demo)
DELETE FROM activity_logs;
DELETE FROM users;
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE activity_logs AUTO_INCREMENT = 1;

-- User 1: Tài khoản bình thường, đầy đủ thông tin
-- username=nguyenvana | password=MyP@ssw0rd2026!
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('nguyenvana', 'Uvc+IxGt4Xr5KfUydCUIdsrimiVCkJ8Nx+q7EMpIhUfVcbScJZKpCsIhSw==', 'ru3u8PstHU/J7x+ogd22OvDzDXSyL4ifQzohmdFKnN6TUZwb31NRyrYsR8Xa6kGj', '$argon2id$v=19$m=102400,t=2,p=8$TwCtAaHEwmUuPc9QXfnMpg$QIZv8m8bC2pxUGu3OzMo5Kb3abCeRlsWcPeyDslD9DE', 'GsLe2bbGxAeRzqzA2b8gknU8PGyjhtW5D15O+9PVDZTaRVxwOqI=', '1dx0uvxYY13nYIX8r6qEqyrwlmcY69Y0sqRXOkFh3MrKzbXBKw/7rg==', 'CT8v8oS3JGEDEo55rVwnqwJt3W4iHUTLJZSBR5vZO6msdBFg2mTv5EAXg/76BQjePAX7/fUnHnRTw+4=', 0, NULL);

-- User 2: Tài khoản thiếu CMND và địa chỉ
-- username=tranthib | password=Secure#Hash99XY
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('tranthib', 'D0cOKsr0noai4X7mcoXNDlNCMGQmz7NoVSpjeixJSAzoWPil4R8RHS9X', 'zqUsDTNdUOTF1oxKZmqi+8VOD8mt7pPic6ZT/vmdWrLBZI8d0RR6H+iWByUgzw==', '$argon2id$v=19$m=102400,t=2,p=8$b2L66KRL+as557nL6UDEEg$WgG8HN4G0WbMn8jcVxc9+2rpoQimHMDTy4gjzt69OkY', 'tAiLviquIZX9OUn6X8Kp8jAxIy3ik08ElxGYXCvDDcro+4oXa7g=', NULL, NULL, 0, NULL);

-- User 3: Tài khoản đang bị KHÓA — demo lockout
-- username=levanc | password=Dragon$Fly2026#
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('levanc', 'Wp+Rqp52kNYZIRWWRI/y/nWTM7c9PsiZE7wCkCx6RzLtdvDzNt8=', 'FtZBUM5BmNlU9i4JhJIUEpmH1JvgoTJiqMi6+VrLpQru+6CMzeFzb89ikXFxBA==', '$argon2id$v=19$m=102400,t=2,p=8$LEP0bpEFg+ZYnI5teS6LBQ$e5LAjtiCHFfDyKD+irGkuKSmZSyJSQdON/f+AwDdpsM', 'A+SLVTXIydxAc+FXcgjuwH17Evs0VFAb35nVBvK+Xz8/Em9UkGI=', 'GGmCgF+c+upGmOdmFBRRrkQFyULpfb0b7PyHE+2G2wIs9DqsqDs1tg==', 'lNpZCN1WYmQpYD/f+2f9f+XXV0io26ewvnd9/l679SVzlez+CJ9+SAHx6iMX4LuVTNZzteY=', 5, DATE_ADD(NOW(), INTERVAL 3 MINUTE));

-- User 4: Tài khoản đã nhập sai 3/5 lần — demo đếm failed attempts
-- username=phamthid | password=CorrectH0rse!99
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('phamthid', 'ZzjJ/Pxdxco9IrXj5gzCXLQQpSqWg1NaErYuHtKnb7Wi/meyuSEa3ZeO', 'RObeCYnlM6+sPyCanm/+MYMOV6sG4yP2vxppC4ufRCxrSWGHQBS7rAOD6eRmVw==', '$argon2id$v=19$m=102400,t=2,p=8$YUOiO20VeulYdT0/lTSQyA$hrZAOJLL/9xW8efBe+kXkIPP6TQyyHqEHdCtEobOefU', 'TeA5cCduP5QhM3dZHSIbJzXD3/RbLHyTeRGlCOmQaAEevTFgelU=', 'u07Qm+6WacC0ycwX8/fth3P4CcSEw4JGFC0tKCvJSZx3hFk7E1keFQ==', NULL, 3, NULL);

-- User 5: Tài khoản dùng để demo đổi mật khẩu
-- username=hoangvane | password=Admin@Secure123!
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('hoangvane', 'd9eeVVbBf/YZAjSfa1TlWM5ekhqSr+CBp0tGuVxbD49uaQQN6SRU1lc=', 'TidENyx5Qf+RKbXtSnF/dFmI8d/vKGp4/10khC7DH0YxpSz2bkcyXUD06jJnz6JB', '$argon2id$v=19$m=102400,t=2,p=8$68PCui0pB1o0IL5gdrdahA$dfXyG2n9Z3pPdPaRHXJ5mrIVO3bRr1KWRK2XSVYwEE8', '0UPr+O9LtFB6x0cXyOPSDX7XX+ZZ4fSkSg3UZZDF4GTJ/iGekmU=', 'XlQ1AjCRJj23Z8Qx8kmKQZs7fNP25+FTRVFKFPiKkiXyV1dKkNxmtA==', '/gK9EezENP4no7clXcUTVzucX9gPqJXNnwkB2X1hcHP5+kM7RqMNtt6B1g3rbLRL2gXT52mbcidZZS3H4Qqra5e2mrt1fKhj', 0, NULL);

-- User 6: Tài khoản sinh viên, không có phone/CMND/address
-- username=vuthif | password=Bl@ckP4nther_99!
INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address, failed_login_attempts, locked_until) VALUES ('vuthif', 'kfxVnF/V8Rid/5T5Lx0n0jsSaRXZgSiMmBViO7uWd92ASQN+nn3W', '2oTJEYgCRg1Tef6h/fzuXRJaNvBL36eDiq0Yfo3vf7wgdAvLPVGYdDFFY6iM28DPMksEzmk=', '$argon2id$v=19$m=102400,t=2,p=8$R6dYc98xAJ4aIplz0Nyaug$B1fdxQcacZnZM7xWfhNUfRoM5vflsf289KVZAuKn38I', NULL, NULL, NULL, 0, NULL);

-- ----------------------------------------------------------------
-- Activity logs mẫu
-- ----------------------------------------------------------------
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (1, 'REGISTER', 'Đăng ký thành công với username=nguyenvana, strength=Strong', '10.0.0.1');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (1, 'LOGIN_SUCCESS', 'Đăng nhập thành công (username=nguyenvana)', '10.0.0.1');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (1, 'UPDATE_PROFILE', 'Cập nhật: phone', '10.0.0.1');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (2, 'REGISTER', 'Đăng ký thành công với username=tranthib, strength=Strong', '192.168.1.5');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (2, 'LOGIN_SUCCESS', 'Đăng nhập thành công (username=tranthib)', '192.168.1.5');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'REGISTER', 'Đăng ký thành công với username=levanc, strength=Strong', '10.0.0.3');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 1/5', '203.0.113.45');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 2/5', '203.0.113.45');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 3/5', '198.51.100.23');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 4/5', '198.51.100.23');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 5/5', '192.0.2.99');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (3, 'LOGIN_LOCKED', 'Tài khoản bị khóa 3 phút do nhập sai 5 lần', '192.0.2.99');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (4, 'REGISTER', 'Đăng ký thành công với username=phamthid, strength=Strong', '10.0.0.4');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (4, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 1/5', '10.0.0.4');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (4, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 2/5', '10.0.0.4');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (4, 'LOGIN_FAILED', 'Sai mật khẩu. Lần thử 3/5', '10.0.0.4');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (5, 'REGISTER', 'Đăng ký thành công với username=hoangvane, strength=Strong', '10.0.0.2');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (5, 'LOGIN_SUCCESS', 'Đăng nhập thành công (username=hoangvane)', '10.0.0.2');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (5, 'CHANGE_PASSWORD', 'Thay đổi mật khẩu thành công', '10.0.0.2');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (6, 'REGISTER', 'Đăng ký thành công với username=vuthif, strength=Strong', '172.16.0.10');
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (6, 'LOGIN_SUCCESS', 'Đăng nhập thành công (username=vuthif)', '172.16.0.10');

-- ================================================================
-- Import vào MySQL:
-- Dán vào MySQL import trực tiếp.
-- ================================================================
