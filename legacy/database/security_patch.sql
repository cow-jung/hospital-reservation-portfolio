USE hospital_project;

-- =========================================================
-- users 보안 관련 컬럼
-- =========================================================

ALTER TABLE users
ADD COLUMN password_changed_at DATETIME
    NOT NULL DEFAULT CURRENT_TIMESTAMP,

ADD COLUMN failed_login_count INT
    NOT NULL DEFAULT 0,

ADD COLUMN locked_until DATETIME
    NULL,

ADD COLUMN last_login_at DATETIME
    NULL,

ADD COLUMN last_login_ip VARCHAR(45)
    NULL;


-- =========================================================
-- 로그인 시도 기록
-- =========================================================

CREATE TABLE IF NOT EXISTS security_logs
(
    log_id BIGINT NOT NULL AUTO_INCREMENT,

    user_id INT NULL,

    username VARCHAR(50) NULL,

    ip_address VARCHAR(45) NOT NULL,

    success BOOLEAN NOT NULL,

    reason VARCHAR(100) NULL,

    created_at DATETIME
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    INDEX idx_security_logs_ip (ip_address),

    INDEX idx_security_logs_created_at (created_at),

    CONSTRAINT security_logs_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);


-- =========================================================
-- IP / CIDR 차단 규칙
-- =========================================================

CREATE TABLE IF NOT EXISTS security_ip_rules
(
    rule_id INT NOT NULL AUTO_INCREMENT,

    network VARCHAR(50) NOT NULL,

    block_scope ENUM('login', 'site')
        NOT NULL DEFAULT 'login',

    description VARCHAR(100) NULL,

    enabled BOOLEAN
        NOT NULL DEFAULT TRUE,

    created_at DATETIME
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (rule_id),

    UNIQUE KEY uq_security_ip_rules_network_scope
        (network, block_scope)
);