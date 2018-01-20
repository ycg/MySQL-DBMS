create database mysql_web;

use mysql_web;
create table host_infos
(
    host_id mediumint unsigned not null auto_increment primary key,
    host varchar(30) not null default '' comment '主机ip地址或主机名',
    port smallint unsigned not null default 3306 comment '端口号',
    user varchar(30) not null default 'root' ,
    password varchar(100) not null default '' comment '密码',
    remark varchar(100) not null default '' comment '备注',
    is_master tinyint not null default 0 comment '是否是主库',
    is_slave tinyint not null default 0 comment '是否是从库',
    master_id mediumint unsigned not null default 0 comment '如果是从库-关联他主库的id',
    ssh_user VARCHAR(20) NOT NULL DEFAULT 'root' COMMENT 'ssh远程执行命令的用户，默认是root',
    ssh_port SMALLINT UNSIGNED NOT NULL DEFAULT 22 COMMENT '用于ssh远程执行的端口',
    ssh_password VARCHAR(100) NOT NULL DEFAULT '' COMMENT '如果不能免密码登录，需要配置密码',
    is_deleted tinyint not null default 0 comment '删除的将不再监控',
    created_time timestamp not null default current_timestamp,
    modified_time timestamp not null default current_timestamp on update current_timestamp
    #UNIQUE KEY idx_host_ip (`host`, `port`) COMMENT 'ip地址和端口号唯一键'
) comment = 'mysql账户信息' CHARSET utf8 ENGINE innodb;

#insert into host_infos (host, port, user, password, remark) values ("192.168.11.128", 3306, "yangcg", "yangcaogui", "Monitor");