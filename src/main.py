# -*- coding: utf-8 -*-

import time
import traceback
import threading
import threadpool

import cache
import entity
import common
import db_util
import settings


class Server(threading.Thread):
    __times = 1
    __thread_pool = threadpool.ThreadPool(settings.THREAD_POOL_SIZE)

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def load_data(self):
        self.set_old_mysql_datas()
        self.check_master_and_slave_relation()

    def run(self):
        while (True):
            time.sleep(settings.UPDATE_INTERVAL)
            requests = threadpool.makeRequests(self.get_mysql_data, list(cache.get_all_host_infos()), None)
            for request in requests:
                self.__thread_pool.putRequest(request)
            if (len(requests) > 0):
                self.__thread_pool.poll()

    def set_old_mysql_datas(self):
        for host_info in cache.get_all_host_infos():
            data_new = self.get_dic_data(host_info, show_global_status_sql)
            cache.set_old_mysql_data(host_info.host_id, data_new)

    def get_mysql_data(self, host_info):
        try:
            # aa = time.time()
            host_id = host_info.host_id
            mysql_data = cache.get_mysql_data_by_host_id(host_id)
            mysql_data.mysql_variables = host_info.mysql_variables
            data_new = self.get_dic_data(host_info, show_global_status_sql)
            cache.set_new_mysql_data(host_id, data_new)

            # set mysql item value
            for item_name in item_names:
                cache.set_item_value(host_id, item_name.lower())

            for item_name in item_names_for_byte:
                cache.set_item_value_for_byte(host_id, item_name.lower())

            for item_name in item_names_for_number:
                cache.set_item_value_for_number(host_id, item_name.lower())

            # get mysql replication
            self.get_mysql_slave_status(host_info)

            # get binlog size total
            total_size = 0
            if (mysql_data.mysql_variables.log_bin == "ON"):
                for row in db_util.fetchall(host_info, "show master logs;"):
                    total_size += int(row["File_size"])
            mysql_data.binlog_size_total = common.convert_for_byte(total_size)

            # mysql data calculate
            mysql_data.uptime = int(data_new["uptime"]) / 60 / 60 / 24
            mysql_data.dml = mysql_data.com_insert + mysql_data.com_update + mysql_data.com_delete
            mysql_data.dirty_page_pct = round(float(mysql_data.innodb_buffer_pool_pages_dirty) / float(mysql_data.innodb_buffer_pool_pages_total) * 100, 2)
            mysql_data.data_page_pct = round(float(mysql_data.innodb_buffer_pool_pages_data) / float(mysql_data.innodb_buffer_pool_pages_total) * 100, 2)
            mysql_data.buffer_pool_hit = (1 - int(data_new["innodb_buffer_pool_reads"]) / (int(data_new["innodb_buffer_pool_read_requests"]) + int(data_new["innodb_buffer_pool_reads"]))) * 100
            if (mysql_data.binlog_cache_use > 0):
                mysql_data.binlog_cache_hit = (1 - mysql_data.binlog_cache_disk_use / mysql_data.binlog_cache_use) * 100
            else:
                mysql_data.binlog_cache_hit = 0

            cache.set_old_mysql_data(host_id, data_new)
            # bb = time.time()
            # print ("{0}-{1}".format(host_id, (bb - aa)))
        except Exception as e:
            traceback.print_exc()

    def get_mysql_slave_status(self, host_info):
        if (host_info.is_slave):
            mysql_data = cache.get_mysql_data_by_host_id(host_info.host_id)
            result = db_util.fetchone(host_info, "show slave status;")
            mysql_data.error_message = result["Last_Error"]
            mysql_data.io_status = result["Slave_IO_Running"]
            mysql_data.sql_status = result["Slave_SQL_Running"]
            mysql_data.master_log_file = result["Master_Log_File"]
            mysql_data.master_log_pos = int(result["Read_Master_Log_Pos"])
            mysql_data.slave_log_file = result["Relay_Master_Log_File"]
            mysql_data.slave_log_pos = int(result["Exec_Master_Log_Pos"])
            mysql_data.slave_retrieved_gtid_set = result["Retrieved_Gtid_Set"].split(",")
            mysql_data.slave_execute_gtid_set = result["Executed_Gtid_Set"].split(",")
            mysql_data.seconds_behind_master = result["Seconds_Behind_Master"] if result["Seconds_Behind_Master"] else 0
            mysql_data.delay_pos_count = mysql_data.master_log_pos - mysql_data.slave_log_pos
            mysql_data.delay_pos_byte = common.convert_for_byte(mysql_data.delay_pos_count)

    def get_dic_data(self, host_info, sql):
        result = {}
        for row in db_util.fetchall(host_info, sql):
            result[row.get("Variable_name").lower()] = row.get("Value")
        return result

    def get_mysql_variables_info(self, host_info):
        info = entity.Entity()
        for row in db_util.fetchall(host_info, show_global_variables_sql):
            setattr(info, row.get("Variable_name").lower(), row.get("Value"))
        return info

    def check_master_and_slave_relation(self):
        # 有的mysql既是主库也是从库，这个要理清逻辑
        uuid_key = "Slave_UUID"
        for host_info in cache.get_all_host_infos():
            result = db_util.fetchall(host_info, "show slave hosts;")


item_names = [
    "Connections",
    "Threads_created",
    "Threads_connected",
    "Threads_running",
    "Open_tables",
    "Open_files",
    "Binlog_cache_use",
    "Binlog_cache_disk_use",
    "Innodb_current_row_locks",
    "Innodb_row_lock_current_waits",
    "Innodb_row_lock_time_avg",
    "Innodb_row_lock_time_max",
    "Innodb_history_list_length",
    "Innodb_log_waits",
    "Innodb_os_log_pending_fsyncs",
    "Innodb_os_log_pending_writes",
    "Innodb_buffer_pool_pages_data",
    "Innodb_buffer_pool_pages_dirty",
    "Innodb_buffer_pool_pages_free",
    "Innodb_buffer_pool_pages_total",
    "Innodb_buffer_pool_wait_free",
    "Innodb_data_pending_fsyncs",
    "Innodb_data_pending_reads",
    "Innodb_data_pending_writes",
    "Innodb_ibuf_size",
    "Innodb_ibuf_free_list",
    "Rpl_semi_sync_slave_status",
    "Rpl_semi_sync_master_status",
    "Rpl_semi_sync_master_clients",
    "Rpl_semi_sync_master_net_waits",
    "Rpl_semi_sync_master_net_wait_time",
    "Rpl_semi_sync_master_tx_waits",
    "Rpl_semi_sync_master_tx_avg_wait_time",
    "Rpl_semi_sync_master_no_tx",
    "Rpl_semi_sync_master_yes_tx",
    "Rpl_semi_sync_master_no_times",
    "Rpl_semi_sync_master_wait_sessions",
]

item_names_for_byte = [
    "Bytes_sent",
    "Bytes_received",
    "Innodb_os_log_written",
    "Innodb_data_read",
    "Innodb_data_written",
]

item_names_for_number = [
    "Uptime",
    "Questions",
    "Com_select",
    "Com_insert",
    "Com_update",
    "Com_delete",
    "Com_commit",
    "Com_rollback",
    "Slow_queries",
    "Connections",
    "Aborted_clients",
    "Aborted_connects",
    "Handler_commit",
    "Handler_rollback",
    "Handler_read_first",
    "Handler_read_key",
    "Handler_read_next",
    "Handler_read_last",
    "Handler_read_rnd",
    "Handler_read_rnd_next",
    "Handler_update",
    "Handler_write",
    "Handler_delete",
    "Opened_tables",
    "Table_open_cache_hits",
    "Table_open_cache_misses",
    "Table_open_cache_overflows",
    "Opened_files",
    "Created_tmp_files",
    "Created_tmp_tables",
    "Created_tmp_disk_tables",
    "Table_locks_immediate",
    "Table_locks_waited",
    "Select_full_join",
    "Select_scan",
    "Select_full_range_join",
    "Select_range_check",
    "Select_range",
    "Sort_merge_passes",
    "Sort_range",
    "Sort_scan",
    "Innodb_row_lock_time",
    "Innodb_deadlocks",
    "Innodb_log_writes",
    "Innodb_log_write_requests",
    "Innodb_os_log_written",
    "Innodb_buffer_pool_pages_flushed",
    "Innodb_rows_read",
    "Innodb_rows_updated",
    "Innodb_rows_deleted",
    "Innodb_rows_inserted",
    "Innodb_buffer_pool_write_requests",
    "Innodb_buffer_pool_reads",
    "Innodb_buffer_pool_read_requests",
    "Innodb_data_reads",
    "Innodb_data_writes",
    "Innodb_data_fsyncs",
    "Innodb_pages_created",
    "Innodb_pages_written",
    "Innodb_pages_read",
    "Innodb_ibuf_merges",
    "Innodb_ibuf_merged_inserts",
    "Innodb_ibuf_merged_deletes",
    "Innodb_ibuf_merged_delete_marks",
    "Innodb_mutex_os_waits",
    "Innodb_mutex_spin_rounds",
    "Innodb_mutex_spin_waits",
    "Innodb_s_lock_os_waits",
    "Innodb_s_lock_spin_rounds",
    "Innodb_s_lock_spin_waits",
    "Innodb_x_lock_os_waits",
    "Innodb_x_lock_spin_rounds",
    "Innodb_x_lock_spin_waits",
    "Innodb_dblwr_writes",
    "Innodb_dblwr_pages_written",
    "Innodb_max_trx_id",
    "Rpl_semi_sync_master_net_wait_time",
    "Rpl_semi_sync_master_tx_wait_time"
]

show_global_variables_sql = """
show global variables where variable_name in
(
'version',
'version_comment',
'server_uuid',
'datadir',
'pid_file',
'binlog_format',
'log_bin',
'sync_binlog',
'log_bin_basename',
'max_connections',
'max_used_connections',
'thread_cache_size',
'table_open_cache',
'table_open_cache_instances',
'innodb_buffer_pool_size',
'innodb_flush_log_at_trx_commit',
'read_only',
'innodb_spin_wait_delay',
'innodb_sync_spin_loops',
'query_cache_type',
'query_cache_size',
'innodb_log_file_size',
'innodb_log_buffer_size',
'innodb_flush_log_at_trx_commit',
'wait_timeout',
'interactive_timeout'
);
"""

show_global_status_sql = "show global status where variable_name in ('{0}','{1}','{2}');".format("','".join(item_names), "','".join(item_names_for_byte), "','".join(item_names_for_number))

if (__name__ == "__main__"):
    my_info = entity.Entity()
    my_info.host_id = 100
    my_info.key = 100
    my_info.host = "localhost"
    my_info.port = 3306
    my_info.user = "timyang"
    my_info.is_slave = False
    my_info.password = "123456"

    while True:
        #get_mysql_data(my_info)
        time.sleep(1)
