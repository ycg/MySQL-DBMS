# -*- coding: utf-8 -*-

import psutil
import pymysql

# web server
host = ""
port = 5000

# mysql config
mysql_host = ""
mysql_user = ""
mysql_port = 3306
mysql_password = ""

connection_pool = None


class Entity():
    def __init__(self):
        pass


def get_linux_info():
    print (psutil.virtual_memory())
    # print (psutil.cpu_times())
    print (psutil.cpu_times_percent())
    # print (psutil.cpu_count())
    print (psutil.cpu_stats())
    print (psutil.virtual_memory())
    # sdiskio(read_count=342846, write_count=1063909, read_bytes=14861657088L, write_bytes=16533497856L, read_time=201L, write_time=636L)
    print (psutil.disk_io_counters())
    aa = psutil.disk_partitions()
    for bb in aa:
        print (psutil.disk_usage(bb.device))
    # print (psutil.disk_usage('C:\\'))
    # print (psutil.disk_io_counters())
    print (psutil.net_io_counters(pernic=True))
    print (psutil.users())
    print (psutil.pids())
    # mysql_process = psutil.Process(16898)
    # print (mysql_process.cpu_percent(), mysql_process.memory_percent())


get_linux_info()


