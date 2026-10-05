-- =========================================================
-- 테스트 계정 비밀번호를 알려진 값으로 재설정
-- =========================================================
-- dump.sql 안의 admin, user1 계정 비밀번호는 원래 값을 알 수 없는
-- 해시라서, 로그인 테스트를 위해 아래 두 계정만 비밀번호를 재설정합니다.
--
--   admin (관리자) : Admin1234!
--   user1 (사용자) : User1234!
--
-- 실행 순서: dump.sql 실행 이후 아무 때나 실행 가능합니다.
-- =========================================================

USE hospital_project;

-- admin 계정 비밀번호 -> Admin1234!
UPDATE users
SET password = 'scrypt:32768:8:1$IQAS0hJNXeIk1mY1$18b3af6ba2f5c88144c2c51e09aa5fb1244106c575598fa9b66877e659ccb4ffac2e76a66573ad8229608f8f94d3aecfd50f1bc74cc3f25dc828aa8e8d8f8ced'
WHERE username = 'admin';

-- user1 계정 비밀번호 -> User1234!
UPDATE users
SET password = 'scrypt:32768:8:1$IkoYLDfIhP8HbSko$d9447bca8216b12b9efa81610f512a1e12751855fc0bc5f6888e6454cdc44f193468764a8dd4050dcde76aa86695331084fa252c6c5306effc456223cebd84c5'
WHERE username = 'user1';
