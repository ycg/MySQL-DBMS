# -*- coding: utf-8 -*-

import pymysql
from entity import Entity
from DBUtils.PooledDB import PooledDB

connection_pools = {}


def execute(host_info, sql):
    connection, cursor = None, None
    try:
        connection, cursor = execute_for_db(host_info, sql)
    finally:
        close(connection, cursor)


def fetchone(host_info, sql):
    connection, cursor = None, None
    try:
        connection, cursor = execute_for_db(host_info, sql)
        return cursor.fetchone()
    finally:
        close(connection, cursor)


def fetchall(host_info, sql):
    connection, cursor = None, None
    try:
        connection, cursor = execute_for_db(host_info, sql)
        return cursor.fetchall()
    finally:
        close(connection, cursor)


def execute_for_cursor(sql, connection=None, cursor=None):
    return cursor_execute(connection, cursor, sql)


def fetchone_for_cursor(sql, connection=None, cursor=None):
    cursor = cursor_execute(connection, cursor, sql)
    return cursor.fetchone()


def fetchall_for_cursor(sql, connection=None, cursor=None):
    cursor = cursor_execute(connection, cursor, sql)
    return cursor.fetchall()


def cursor_execute(connection, cursor, sql):
    if (cursor is None):
        cursor = connection.cursor()
    cursor.execute(sql)
    return cursor


def close(connection, cursor):
    if (cursor is not None):
        cursor.close()
    if (connection is not None):
        connection.commit()
        connection.close()


def execute_for_db(host_info, sql):
    connection, cursor = get_conn_and_cur(host_info)
    cursor.execute(sql)
    return connection, cursor


def get_conn_and_cur(host_info):
    connection = get_mysql_connection(host_info)
    cursor = connection.cursor()
    return connection, cursor


def get_mysql_connection(host_info):
    if (connection_pools.get(host_info.key) is None):
        pool = PooledDB(creator=pymysql, mincached=4, maxcached=8, maxconnections=10,
                        host=host_info.host, port=host_info.port, user=host_info.user, passwd=host_info.password,
                        use_unicode=False, charset="utf8", cursorclass=pymysql.cursors.DictCursor, reset=False, autocommit=True,
                        connect_timeout=1, read_timeout=10, write_timeout=10)
        connection_pools[host_info.key] = pool
    return connection_pools[host_info.key].connection()


def get_list_infos(host_info, sql):
    result = []
    for row in fetchall(host_info, sql):
        info = Entity()
        for key, value in row.items():
            setattr(info, key, value)
        result.append(info)
    return result


def get_info_to_lower(host_info, sql):
    info = Entity
    obj_row = fetchone(host_info, sql)
    if (obj_row is not None):
        for key, value in obj_row.items():
            setattr(info, key.lower(), value)
    return info


def get_list_infos_to_lower(host_info, sql):
    result = []
    for row in fetchall(host_info, sql):
        info = Entity()
        for key, value in row.items():
            setattr(info, key.lower(), value)
        result.append(info)
    return result


def escape(string):
    return pymysql.escape_string(string)


def execute_sql(ip, port, user, password, sql):
    connection, cursor = None, None
    try:
        connection = pymysql.connect(host=ip, user=user, passwd=password, port=port, use_unicode=True, charset="utf8", connect_timeout=1)
        cursor = connection.cursor()
        cursor.execute(sql)
    finally:
        if (cursor is not None):
            cursor.close()
        if (connection is not None):
            connection.close()
