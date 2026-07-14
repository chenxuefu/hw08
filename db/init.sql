DROP DATABASE IF EXISTS wheat_pest_db;
CREATE DATABASE wheat_pest_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wheat_pest_db;

CREATE TABLE sys_user (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    last_login_time DATETIME DEFAULT NULL,
    last_login_ip VARCHAR(50) DEFAULT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    KEY idx_email (email),
    KEY idx_phone (phone),
    KEY idx_status (status),
    KEY idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_role (
    id BIGINT NOT NULL AUTO_INCREMENT,
    role_code VARCHAR(50) NOT NULL,
    role_name VARCHAR(50) NOT NULL,
    data_scope VARCHAR(20) NOT NULL DEFAULT 'DATA_SELF',
    description VARCHAR(255) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_code (role_code),
    UNIQUE KEY uk_role_name (role_name),
    KEY idx_sys_role_status (status),
    KEY idx_sys_role_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_permission (
    id BIGINT NOT NULL AUTO_INCREMENT,
    perm_code VARCHAR(100) NOT NULL,
    perm_name VARCHAR(100) NOT NULL,
    perm_type VARCHAR(20) NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_perm_code (perm_code),
    KEY idx_perm_code (perm_code),
    KEY idx_perm_type (perm_type),
    KEY idx_sys_permission_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_menu (
    id BIGINT NOT NULL AUTO_INCREMENT,
    parent_id BIGINT NOT NULL DEFAULT 0,
    menu_name VARCHAR(50) NOT NULL,
    menu_path VARCHAR(200) NOT NULL,
    menu_icon VARCHAR(100) DEFAULT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    visible TINYINT NOT NULL DEFAULT 1,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_parent_id (parent_id),
    KEY idx_sys_menu_path (menu_path),
    KEY idx_sys_menu_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_user_role (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_role (user_id, role_id),
    KEY idx_sys_user_role_user_id (user_id),
    KEY idx_sys_user_role_role_id (role_id),
    KEY idx_sys_user_role_is_deleted (is_deleted),
    CONSTRAINT fk_sys_user_role_user FOREIGN KEY (user_id) REFERENCES sys_user (id),
    CONSTRAINT fk_sys_user_role_role FOREIGN KEY (role_id) REFERENCES sys_role (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_role_permission (
    id BIGINT NOT NULL AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_perm (role_id, permission_id),
    KEY idx_sys_role_permission_role_id (role_id),
    KEY idx_sys_role_permission_permission_id (permission_id),
    KEY idx_sys_role_permission_is_deleted (is_deleted),
    CONSTRAINT fk_sys_role_permission_role FOREIGN KEY (role_id) REFERENCES sys_role (id),
    CONSTRAINT fk_sys_role_permission_permission FOREIGN KEY (permission_id) REFERENCES sys_permission (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_role_menu (
    id BIGINT NOT NULL AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    menu_id BIGINT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_menu (role_id, menu_id),
    KEY idx_sys_role_menu_role_id (role_id),
    KEY idx_sys_role_menu_menu_id (menu_id),
    KEY idx_sys_role_menu_is_deleted (is_deleted),
    CONSTRAINT fk_sys_role_menu_role FOREIGN KEY (role_id) REFERENCES sys_role (id),
    CONSTRAINT fk_sys_role_menu_menu FOREIGN KEY (menu_id) REFERENCES sys_menu (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE detection_batch (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    batch_name VARCHAR(100) NOT NULL,
    total_images INT NOT NULL DEFAULT 0,
    processed_images INT NOT NULL DEFAULT 0,
    success_images INT NOT NULL DEFAULT 0,
    failed_images INT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 0,
    start_time DATETIME DEFAULT NULL,
    end_time DATETIME DEFAULT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_detection_batch_user_id (user_id),
    KEY idx_detection_batch_status (status),
    KEY idx_detection_batch_create_time (create_time),
    KEY idx_detection_batch_is_deleted (is_deleted),
    CONSTRAINT fk_detection_batch_user FOREIGN KEY (user_id) REFERENCES sys_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE model_version (
    id BIGINT NOT NULL AUTO_INCREMENT,
    version_code VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    weight_path VARCHAR(500) NOT NULL,
    map_50 DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    map_50_95 DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    precision_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    recall_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    is_active TINYINT NOT NULL DEFAULT 0,
    description VARCHAR(500) DEFAULT NULL,
    create_by BIGINT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_version_code (version_code),
    KEY idx_model_version_code (version_code),
    KEY idx_model_version_is_active (is_active),
    KEY idx_model_version_create_by (create_by),
    KEY idx_model_version_is_deleted (is_deleted),
    CONSTRAINT fk_model_version_user FOREIGN KEY (create_by) REFERENCES sys_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE detection_record (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    batch_id BIGINT DEFAULT NULL,
    image_path VARCHAR(500) NOT NULL,
    result_image_path VARCHAR(500) DEFAULT NULL,
    image_name VARCHAR(255) NOT NULL,
    image_size BIGINT NOT NULL DEFAULT 0,
    image_width INT NOT NULL DEFAULT 0,
    image_height INT NOT NULL DEFAULT 0,
    total_detections INT NOT NULL DEFAULT 0,
    avg_confidence DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    inference_time_ms INT NOT NULL DEFAULT 0,
    model_version_id BIGINT NOT NULL,
    status TINYINT NOT NULL DEFAULT 0,
    error_message VARCHAR(500) DEFAULT NULL,
    detection_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_batch_id (batch_id),
    KEY idx_detection_record_status (status),
    KEY idx_detection_time (detection_time),
    KEY idx_model_version_id (model_version_id),
    KEY idx_detection_record_is_deleted (is_deleted),
    CONSTRAINT fk_detection_record_user FOREIGN KEY (user_id) REFERENCES sys_user (id),
    CONSTRAINT fk_detection_record_batch FOREIGN KEY (batch_id) REFERENCES detection_batch (id),
    CONSTRAINT fk_detection_record_model FOREIGN KEY (model_version_id) REFERENCES model_version (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE detection_result (
    id BIGINT NOT NULL AUTO_INCREMENT,
    record_id BIGINT NOT NULL,
    class_id INT NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    class_name_cn VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    bbox_x DECIMAL(10,2) NOT NULL,
    bbox_y DECIMAL(10,2) NOT NULL,
    bbox_w DECIMAL(10,2) NOT NULL,
    bbox_h DECIMAL(10,2) NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_record_id (record_id),
    KEY idx_class_id (class_id),
    KEY idx_detection_result_is_deleted (is_deleted),
    CONSTRAINT fk_detection_result_record FOREIGN KEY (record_id) REFERENCES detection_record (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE disease_info (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_name VARCHAR(50) NOT NULL,
    chinese_name VARCHAR(50) NOT NULL,
    alias VARCHAR(200) DEFAULT NULL,
    symptom TEXT NOT NULL,
    cause TEXT NOT NULL,
    prevention TEXT NOT NULL,
    example_image VARCHAR(500) DEFAULT NULL,
    severity_level TINYINT NOT NULL DEFAULT 1,
    create_by BIGINT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_class_name (class_name),
    KEY idx_disease_class_name (class_name),
    KEY idx_disease_chinese_name (chinese_name),
    KEY idx_disease_create_by (create_by),
    KEY idx_disease_is_deleted (is_deleted),
    CONSTRAINT fk_disease_info_user FOREIGN KEY (create_by) REFERENCES sys_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_login_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT DEFAULT NULL,
    username VARCHAR(50) NOT NULL,
    login_ip VARCHAR(50) NOT NULL,
    login_location VARCHAR(100) DEFAULT NULL,
    browser VARCHAR(100) DEFAULT NULL,
    os VARCHAR(100) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    message VARCHAR(255) DEFAULT NULL,
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_sys_login_log_user_id (user_id),
    KEY idx_sys_login_log_username (username),
    KEY idx_sys_login_log_login_ip (login_ip),
    KEY idx_sys_login_log_status (status),
    KEY idx_sys_login_log_login_time (login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_operation_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    username VARCHAR(50) NOT NULL,
    module VARCHAR(50) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_url VARCHAR(500) NOT NULL,
    request_params TEXT DEFAULT NULL,
    response_code INT NOT NULL DEFAULT 0,
    ip VARCHAR(50) NOT NULL,
    cost_ms INT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    operation_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_sys_operation_log_user_id (user_id),
    KEY idx_sys_operation_log_module (module),
    KEY idx_sys_operation_log_status (status),
    KEY idx_sys_operation_log_time (operation_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sys_audit_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    username VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    before_value TEXT DEFAULT NULL,
    after_value TEXT DEFAULT NULL,
    ip VARCHAR(50) NOT NULL,
    audit_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_sys_audit_log_user_id (user_id),
    KEY idx_sys_audit_log_target_type (target_type),
    KEY idx_sys_audit_log_target_id (target_id),
    KEY idx_sys_audit_log_action (action),
    KEY idx_sys_audit_log_time (audit_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO sys_role (id, role_code, role_name, data_scope, description, status, is_deleted) VALUES
(1, 'ROLE_ADMIN', '超级管理员', 'DATA_ALL', '系统管理员', 1, 0),
(2, 'ROLE_EXPERT', '农业专家', 'DATA_ALL', '农业专家', 1, 0),
(3, 'ROLE_USER', '普通用户', 'DATA_SELF', '普通农户', 1, 0);

INSERT INTO sys_user (id, username, password, real_name, email, phone, status, is_deleted) VALUES
(1, 'admin', '$2b$12$Hs7sQ.sc.sxAHYuK1W8ITu2AgvlqhxuQ/qLkd.XrG.1Q9CKwv0uie', '系统管理员', 'admin@wheat.local', '13800000001', 1, 0),
(2, 'expert', '$2b$12$Hs7sQ.sc.sxAHYuK1W8ITu2AgvlqhxuQ/qLkd.XrG.1Q9CKwv0uie', '农业专家', 'expert@wheat.local', '13800000002', 1, 0),
(3, 'farmer', '$2b$12$Hs7sQ.sc.sxAHYuK1W8ITu2AgvlqhxuQ/qLkd.XrG.1Q9CKwv0uie', '种植农户', 'farmer@wheat.local', '13800000003', 1, 0);

INSERT INTO sys_user_role (id, user_id, role_id, is_deleted) VALUES
(1, 1, 1, 0),
(2, 2, 2, 0),
(3, 3, 3, 0);

INSERT INTO sys_permission (id, perm_code, perm_name, perm_type, is_deleted) VALUES
(1, 'user:list', '用户列表', 'BUTTON', 0),
(2, 'user:detail', '用户详情', 'BUTTON', 0),
(3, 'user:create', '用户新增', 'BUTTON', 0),
(4, 'user:update', '用户更新', 'BUTTON', 0),
(5, 'user:delete', '用户删除', 'BUTTON', 0),
(6, 'user:reset-password', '用户重置密码', 'BUTTON', 0),
(7, 'role:list', '角色列表', 'BUTTON', 0),
(8, 'role:detail', '角色详情', 'BUTTON', 0),
(9, 'role:create', '角色新增', 'BUTTON', 0),
(10, 'role:update', '角色更新', 'BUTTON', 0),
(11, 'role:delete', '角色删除', 'BUTTON', 0),
(12, 'menu:list', '菜单列表', 'BUTTON', 0),
(13, 'menu:detail', '菜单详情', 'BUTTON', 0),
(14, 'menu:create', '菜单新增', 'BUTTON', 0),
(15, 'menu:update', '菜单更新', 'BUTTON', 0),
(16, 'menu:delete', '菜单删除', 'BUTTON', 0),
(17, 'detection:single:execute', '单张检测', 'BUTTON', 0),
(18, 'detection:record:list', '检测记录列表', 'BUTTON', 0),
(19, 'detection:record:detail', '检测记录详情', 'BUTTON', 0),
(20, 'detection:record:delete', '检测记录删除', 'BUTTON', 0),
(21, 'detection:record:download', '检测记录下载', 'BUTTON', 0),
(22, 'detection:batch:execute', '批量检测提交', 'BUTTON', 0),
(23, 'detection:batch:list', '批量检测列表', 'BUTTON', 0),
(24, 'detection:batch:detail', '批量检测详情', 'BUTTON', 0),
(25, 'detection:batch:download', '批量报告下载', 'BUTTON', 0),
(26, 'detection:batch:delete', '批量任务删除', 'BUTTON', 0),
(27, 'disease:list', '病害列表', 'BUTTON', 0),
(28, 'disease:detail', '病害详情', 'BUTTON', 0),
(29, 'disease:create', '病害新增', 'BUTTON', 0),
(30, 'disease:update', '病害更新', 'BUTTON', 0),
(31, 'disease:delete', '病害删除', 'BUTTON', 0),
(32, 'dashboard:view', '统计看板查看', 'BUTTON', 0),
(33, 'model:list', '模型列表', 'BUTTON', 0),
(34, 'model:detail', '模型详情', 'BUTTON', 0),
(35, 'model:create', '模型新增', 'BUTTON', 0),
(36, 'model:update', '模型更新', 'BUTTON', 0),
(37, 'model:activate', '模型启用', 'BUTTON', 0),
(38, 'model:delete', '模型删除', 'BUTTON', 0),
(39, 'log:login:list', '登录日志列表', 'BUTTON', 0),
(40, 'log:operation:list', '操作日志列表', 'BUTTON', 0),
(41, 'log:audit:list', '审计日志列表', 'BUTTON', 0);

INSERT INTO sys_menu (id, parent_id, menu_name, menu_path, menu_icon, sort_order, visible, is_deleted) VALUES
(1, 0, '门户首页', '/index.html', 'fa-house', 1, 1, 0),
(2, 0, '登录页', '/pages/login.html', 'fa-right-to-bracket', 2, 1, 0),
(3, 0, '单张检测', '/pages/detection_single.html', 'fa-image', 3, 1, 0),
(4, 0, '批量检测', '/pages/detection_batch.html', 'fa-images', 4, 1, 0),
(5, 0, '检测历史', '/pages/history.html', 'fa-clock-rotate-left', 5, 1, 0),
(6, 0, '检测详情', '/pages/history_detail.html', 'fa-file-lines', 6, 1, 0),
(7, 0, '病害知识库', '/pages/disease_library.html', 'fa-book', 7, 1, 0),
(8, 0, '病害编辑', '/pages/disease_edit.html', 'fa-pen', 8, 1, 0),
(9, 0, '统计看板', '/pages/dashboard.html', 'fa-chart-simple', 9, 1, 0),
(10, 0, '用户管理', '/pages/user_manage.html', 'fa-users', 10, 1, 0),
(11, 0, '角色管理', '/pages/role_manage.html', 'fa-user-shield', 11, 1, 0),
(12, 0, '菜单管理', '/pages/menu_manage.html', 'fa-table-list', 12, 1, 0),
(13, 0, '登录日志', '/pages/login_log.html', 'fa-right-to-bracket', 13, 1, 0),
(14, 0, '操作日志', '/pages/operation_log.html', 'fa-list-check', 14, 1, 0),
(15, 0, '审计日志', '/pages/audit_log.html', 'fa-shield-halved', 15, 1, 0),
(16, 0, '模型版本', '/pages/model_version.html', 'fa-microchip', 16, 1, 0),
(17, 0, '个人中心', '/pages/profile.html', 'fa-id-card', 17, 1, 0);

INSERT INTO sys_role_permission (id, role_id, permission_id, is_deleted) VALUES
(1, 1, 1, 0),(2, 1, 2, 0),(3, 1, 3, 0),(4, 1, 4, 0),(5, 1, 5, 0),(6, 1, 6, 0),
(7, 1, 7, 0),(8, 1, 8, 0),(9, 1, 9, 0),(10, 1, 10, 0),(11, 1, 11, 0),
(12, 1, 12, 0),(13, 1, 13, 0),(14, 1, 14, 0),(15, 1, 15, 0),(16, 1, 16, 0),
(17, 1, 17, 0),(18, 1, 18, 0),(19, 1, 19, 0),(20, 1, 20, 0),(21, 1, 21, 0),
(22, 1, 22, 0),(23, 1, 23, 0),(24, 1, 24, 0),(25, 1, 25, 0),(26, 1, 26, 0),
(27, 1, 27, 0),(28, 1, 28, 0),(29, 1, 29, 0),(30, 1, 30, 0),(31, 1, 31, 0),
(32, 1, 32, 0),(33, 1, 33, 0),(34, 1, 34, 0),(35, 1, 35, 0),(36, 1, 36, 0),
(37, 1, 37, 0),(38, 1, 38, 0),(39, 1, 39, 0),(40, 1, 40, 0),(41, 1, 41, 0),
(42, 2, 17, 0),(43, 2, 18, 0),(44, 2, 19, 0),(45, 2, 20, 0),(46, 2, 21, 0),
(47, 2, 22, 0),(48, 2, 23, 0),(49, 2, 24, 0),(50, 2, 25, 0),(51, 2, 26, 0),
(52, 2, 27, 0),(53, 2, 28, 0),(54, 2, 29, 0),(55, 2, 30, 0),(56, 2, 32, 0),
(57, 3, 17, 0),(58, 3, 18, 0),(59, 3, 19, 0),(60, 3, 20, 0),(61, 3, 21, 0),
(62, 3, 22, 0),(63, 3, 23, 0),(64, 3, 24, 0),(65, 3, 25, 0),(66, 3, 26, 0),
(67, 3, 27, 0),(68, 3, 28, 0);

INSERT INTO sys_role_menu (id, role_id, menu_id, is_deleted) VALUES
(1, 1, 1, 0),(2, 1, 3, 0),(3, 1, 4, 0),(4, 1, 5, 0),(5, 1, 6, 0),(6, 1, 7, 0),
(7, 1, 8, 0),(8, 1, 9, 0),(9, 1, 10, 0),(10, 1, 11, 0),(11, 1, 12, 0),(12, 1, 13, 0),
(13, 1, 14, 0),(14, 1, 15, 0),(15, 1, 16, 0),(16, 1, 17, 0),
(17, 2, 1, 0),(18, 2, 3, 0),(19, 2, 4, 0),(20, 2, 5, 0),(21, 2, 6, 0),(22, 2, 7, 0),
(23, 2, 8, 0),(24, 2, 9, 0),(25, 2, 17, 0),
(26, 3, 1, 0),(27, 3, 3, 0),(28, 3, 4, 0),(29, 3, 5, 0),(30, 3, 6, 0),(31, 3, 7, 0),(32, 3, 17, 0);

INSERT INTO disease_info (id, class_name, chinese_name, alias, symptom, cause, prevention, example_image, severity_level, create_by, is_deleted) VALUES
(1, 'rust', '锈病', '叶锈病', '叶片出现橙黄色至褐色锈斑，后期扩散连片。', '高湿度和温差较大环境下病原菌扩散加快。', '选用抗病品种，及时清除病残体，必要时喷施三唑类药剂。', 'uploads/2026/04/22/disease_rust.jpg', 3, 1, 0),
(2, 'smut', '黑穗病', '穗部黑粉病', '穗部组织膨大变黑并产生黑色粉末。', '带菌种子和土壤病原残留导致侵染。', '播前药剂拌种，加强轮作并及时清除病株。', 'uploads/2026/04/22/disease_smut.jpg', 3, 1, 0),
(3, 'healthy', '健康叶', '正常叶片', '叶色均匀，组织完整，无明显病斑虫孔。', '植株处于正常生长状态。', '继续保持合理灌溉和水肥管理，加强田间巡查。', 'uploads/2026/04/22/disease_healthy.jpg', 1, 1, 0),
(4, 'aphid', '蚜虫', '麦蚜', '叶背或嫩穗聚集大量小型害虫，叶片卷曲发黄。', '温暖干燥条件下蚜虫繁殖速度快。', '利用天敌防治并结合低毒高效药剂轮换施用。', 'uploads/2026/04/22/disease_aphid.jpg', 2, 1, 0);

INSERT INTO model_version (id, version_code, model_name, weight_path, map_50, map_50_95, precision_rate, recall_rate, is_active, description, create_by, is_deleted) VALUES
(1, 'v1.0.0', 'RT-DETR Wheat Baseline', 'backend/weights/rtdetr_wheat_best.pth', 0.9123, 0.7564, 0.9012, 0.8876, 1, '系统初始模型版本', 1, 0);
