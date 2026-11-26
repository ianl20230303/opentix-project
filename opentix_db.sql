SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS opentix_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE opentix_db;

DROP TABLE IF EXISTS opentix_tickets_history;
DROP TABLE IF EXISTS opentix_tickets_latest;

CREATE TABLE opentix_tickets_history (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '編號',
    EVENT_NAME VARCHAR(255) NOT NULL COMMENT '活動名稱',
    EVENT_TIME VARCHAR(100) NOT NULL COMMENT '演出時間',
    REMAIN_SEATS INT NOT NULL COMMENT '剩餘席次',
    PRICE INT NOT NULL COMMENT '票價',
    CREATED_AT DATETIME DEFAULT NOW() COMMENT '爬取紀錄時間'
) COMMENT = 'OPENTIX 歷史售票狀況表';

CREATE TABLE opentix_tickets_latest (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '編號',
    EVENT_NAME VARCHAR(255) NOT NULL COMMENT '活動名稱',
    EVENT_TIME VARCHAR(100) NOT NULL COMMENT '演出時間',
    REMAIN_SEATS INT NOT NULL COMMENT '剩餘席次',
    PRICE INT NOT NULL COMMENT '票價',
    UPDATED_AT DATETIME DEFAULT NOW() COMMENT '最新更新時間'
) COMMENT = 'OPENTIX 最新票況表';


"""
-- 1. 檢查兩張表的總資料筆數
SELECT '最新表 (latest)' AS 表名, COUNT(*) AS 總筆數, MIN(UPDATED_AT) AS 最早時間, MAX(UPDATED_AT) AS 最新時間
FROM opentix_tickets_latest
UNION ALL
SELECT '歷史表 (history)' AS 表名, COUNT(*) AS 總筆數, MIN(CREATED_AT) AS 最早時間, MAX(CREATED_AT) AS 最新時間
FROM opentix_tickets_history;
"""