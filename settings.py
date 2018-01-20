# -*- coding: utf-8 -*-

import platform
from src.entity import Entity

PORT = 5500
IP = "0.0.0.0"

MySQL_Host = Entity()
MySQL_Host.key = 0
MySQL_Host.host = "localhost"
MySQL_Host.port = 3306
MySQL_Host.user = "timyang"
MySQL_Host.password = "123456"

ONE_DAY = 24 * 60 * 60
UPDATE_INTERVAL = 4
THREAD_POOL_SIZE = 50
REPORT_INTERVAL = ONE_DAY
TABLE_CHECK_INTERVAL = ONE_DAY

EMAIL_HOST = ""
EMAIL_PORT = 25
EMAIL_USER = ""
EMAIL_PASSWORD = ""
EMAIL_SEND_USERS = ""

LINUX_OS = 'Linux' in platform.system()
WINDOWS_OS = 'Windows' in platform.system()

BACKUP_ING = 1
BACKUP_SUCCESS = 2
BACKUP_ERROR = 3

BACKUP_TOOL_MYDUMPER = 1
BACKUP_TOOL_MYSQLDUMP = 2
BACKUP_TOOL_XTRABACKUP = 3

BACKUP_MODE_FULL = 1
BACKUP_MODE_INCREMENT = 2

IS_INSERT_MONITOR_LOG = False

MY_KEY = 20

V_MySQL = 1
V_Percona = 2
V_Mariadb = 3
