# -*- coding: utf-8 -*-

import collections

import main
import entity
import common
import db_util
import settings
import algorithm

host_infos = collections.OrderedDict()
mysql_data = collections.OrderedDict()
mysql_data_old = collections.OrderedDict()
mysql_data_new = collections.OrderedDict()


def load_host_infos():
    obj_list = db_util.get_list_infos_to_lower(settings.MySQL_Host, "select * from mysql_web.host_infos;")
    for obj in obj_list:
        obj.master_host_id = 0
        obj.key = obj.host_id
        obj.is_slave = bool(obj.is_slave)
        obj.is_master = bool(obj.is_master)
        #obj.user = algorithm.decrypt(settings.MY_KEY, obj.user)
        #obj.password = algorithm.decrypt(settings.MY_KEY, obj.password)
        #obj.ssh_password = algorithm.decrypt(settings.MY_KEY, obj.ssh_password) if (len(obj.ssh_password) > 0) else None
        host_infos[obj.host_id] = obj
        mysql_data[obj.host_id] = entity.Entity()
        mysql_data[obj.host_id].host_info = obj
        get_mysql_variables(obj)


def get_all_host_infos():
    return host_infos.values()


def get_all_mysql_datas():
    return mysql_data.values()


def get_old_mysql_data(host_id):
    if (host_id not in mysql_data_old.keys()):
        return None
    return mysql_data_old[host_id]


def get_mysql_data_by_host_id(host_id):
    return mysql_data[host_id]


def set_old_mysql_data(host_id, item_values):
    mysql_data_old[host_id] = item_values


def set_new_mysql_data(host_id, item_values):
    mysql_data_new[host_id] = item_values


def set_item_value(host_id, item_name):
    obj_info = mysql_data[host_id]
    data_new = mysql_data_new[host_id]
    if (item_name not in data_new.keys()):
        setattr(obj_info, item_name, 0)
    else:
        setattr(obj_info, item_name, int(data_new[item_name]))


def set_item_value_for_number(host_id, item_name):
    obj_info = mysql_data[host_id]
    data_new = mysql_data_new[host_id]
    data_old = mysql_data_old[host_id]
    if (item_name not in data_new.keys()):
        setattr(obj_info, item_name, 0)
    else:
        item_value = int((int(data_new[item_name]) - int(data_old[item_name])) / settings.UPDATE_INTERVAL)
        setattr(obj_info, item_name, item_value)


def set_item_value_for_byte(host_id, item_name):
    obj_info = mysql_data[host_id]
    data_new = mysql_data_new[host_id]
    data_old = mysql_data_old[host_id]
    if (item_name not in data_new.keys()):
        setattr(obj_info, item_name, 0)
    else:
        item_value = common.convert_for_byte((int(data_new[item_name]) - int(data_old[item_name])) / settings.UPDATE_INTERVAL)
        setattr(obj_info, item_name, item_value)


def get_mysql_variables(host_info):
    host_info.mysql_variables = entity.Entity()
    for row in db_util.fetchall(host_info, main.show_global_variables_sql):
        setattr(host_info.mysql_variables, row.get("Variable_name").lower(), row.get("Value"))

