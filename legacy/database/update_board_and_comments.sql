/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

/*
====================================================================
[최종] 게시판(board) 및 댓글(board_comments) 통합 초기화 스크립트
====================================================================
- 작성자 및 조회수 최신화 완료
- 모든 게시글을 작성 시간(created_at) 기준으로 1번부터 14번까지 재정렬
- 재정렬된 게시글 번호에 맞추어 모든 댓글(7개) 완벽 재매핑 완료
- 기존 테이블 삭제 후 재생성하므로 에러 없이 안전하게 덮어쓰기 가능
====================================================================
*/

-- 1. 자식 테이블(댓글) 먼저 삭제 후 부모 테이블(게시판) 삭제
DROP TABLE IF EXISTS `board_comments`;
DROP TABLE IF EXISTS `board`;

-- 2. 게시판(board) 테이블 생성
CREATE TABLE `board` (
  `board_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `view_count` int NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_secret` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`board_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `board_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 댓글(board_comments) 테이블 생성
CREATE TABLE `board_comments` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `board_id` int NOT NULL,
  `user_id` int NOT NULL,
  `content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  KEY `board_id` (`board_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `board_comments_ibfk_1` FOREIGN KEY (`board_id`) REFERENCES `board` (`board_id`) ON DELETE CASCADE,
  CONSTRAINT `board_comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =========================================================
-- 4. 게시판 데이터 삽입 (시간순으로 1~14번 재정렬 완료)
-- =========================================================
LOCK TABLES `board` WRITE;
INSERT INTO `board` VALUES
(1, 2, '예약 변경은 어떻게 하나요?', '이미 잡은 예약 시간을 변경하고 싶은데 마이페이지에서 가능한가요?', 15, '2026-08-11 09:15:00', 0),
(2, 2, '공휴일에도 진료하나요?', '공휴일에도 진료가 가능한지 궁금합니다.', 59, '2026-08-11 09:29:31', 0),
(3, 2, '입원 관련 문의', '입원시 보호자가 상주할 수 있는지 궁금합니다.', 52, '2026-08-11 09:32:43', 0),
(4, 2, '주차장 이용 안내 부탁드립니다', '병원 방문 시 주차 가능한지, 요금은 어떻게 되는지 궁금합니다.', 11, '2026-08-11 14:30:00', 0),
(5, 2, '진료비 관련 문의입니다', '건강보험 적용 여부와 예상 진료비를 미리 알 수 있을까요?', 7, '2026-08-12 10:05:00', 1),
(6, 1, '홈페이지 이용 팁 공유드립니다', '온라인 예약 시 과거 이력으로 재예약하면 더 빠르게 예약할 수 있어요.', 23, '2026-08-12 16:40:00', 0),
(7, 2, '건강검진 문의', '건강검진 가능한 날짜 문의드립니다. 다음 주에 검진을 받고 싶은데 제일 빠른 날짜가 언제일까요?', 7, '2026-08-13 16:46:50', 0),
(8, 2, '임플란트 비용이 궁금합니다.', '임플란트 비용이 대략 얼마일까요?', 0, '2026-08-13 16:49:54', 1),
(9, 2, '수술 일정 변경', '수술 일정이 현재 8월 28일인데요, 9월 이후로 변경하고 싶습니다. 혹시 9월 둘째 주 정도에 가능할까요?', 0, '2026-08-13 16:52:00', 1),
(10, 2, '피부과 시술 문의', '화상 흉터 치료도 가능할까요?', 3, '2026-08-13 16:54:10', 0),
(11, 2, '아동 예방 접종 문의', '안녕하세요, 예방 접종 시기가 궁금해서 문의드립니다. 4살 아동의 경우 어떤 예방 접종을 하는 것이 좋을까요?', 2, '2026-08-13 16:58:04', 1),
(12, 2, '정형외과 재활 치료 문의', '허리디스크 재활 치료는 어떻게 진행되나요? 병원 내에 재활 운동 센터가 있는지도 궁금해요', 4, '2026-08-13 17:01:11', 0),
(13, 2, '건강 보험 관련해서 질문드립니다.', '증상이 있어서 대장내시경을 받으면 건강 보험이 적용될까요?', 8, '2026-08-13 17:03:16', 1),
(14, 2, '입원 중 식단 문의드려요', '혹시 입원 예정일인 9월달 식단표를 알 수 있을까요? \r\n특정 음식 알레르기가 있어서 미리 알고 싶습니다.', 7, '2026-08-13 17:06:29', 1);
UNLOCK TABLES;

-- =========================================================
-- 5. 댓글 데이터 삽입 (새로 바뀐 게시글 번호에 맞춰 재매핑 완료)
-- =========================================================
LOCK TABLES `board_comments` WRITE;
INSERT INTO `board_comments` (comment_id, board_id, user_id, content, created_at) VALUES
(1, 2, 2, '저도 궁금해요!', '2026-08-11 09:30:40'),
(2, 2, 1, '네, 오후 3시까지 진료합니다.', '2026-08-12 16:59:09'),
(3, 1, 1, '마이페이지 > 예약조회에서 변경 가능합니다. 진료 하루 전까지만 가능한 점 참고해주세요.', '2026-08-11 10:00:00'),
(4, 4, 1, '병원 지하 1~2층 주차장을 무료로 이용하실 수 있습니다.', '2026-08-11 15:10:00'),
(5, 6, 2, '오 좋은 정보 감사합니다!', '2026-08-12 17:00:00'),
(6, 3, 1, '보호자는 1인까지 상주 가능합니다.', '2026-08-18 09:37:41'),
(7, 5, 1, '안내과로 전화 주시면 자세히 안내드리겠습니다.', '2026-08-18 09:38:15');
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;