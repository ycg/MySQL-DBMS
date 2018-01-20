# -*- coding: utf-8 -*-

import json
import os
import gzip
import StringIO
import base64
import sys

from flask_admin import Admin, BaseView, expose
from flask_compress import Compress
from flask import Flask, render_template, request, app, redirect, url_for
from flask_login import login_user, login_required, logout_user, LoginManager, current_user

import settings
from src import cache, main, common
from admin import views

reload(sys)
sys.setdefaultencoding("UTF-8")
compress = Compress()
flask_app = Flask("mysql_web", instance_relative_config=True, instance_path=os.getcwd())
flask_app.config["SECRET_KEY"] = os.urandom(24)
flask_app.config["SESSION_COOKIE_NAME"] = "MySQL-DBMS"
cache.load_host_infos()
server = main.Server()
server.load_data()
server.start()
compress = Compress(flask_app)
admin = Admin(app=flask_app, name="mysql admin")
admin.add_view(views.MyView(name="My View"))


@flask_app.route("/", methods=["GET", "POST"])
def root():
    return render_template("home.html")


@flask_app.route("/data/os", methods=["GET", "POST"])
def get_os_status():
    return render_template("mysql_os.html", mysql_datas=get_mysql_datas())


@flask_app.route("/data/common", methods=["GET", "POST"])
def get_common_status():
    return render_template("mysql_common.html", mysql_datas=get_mysql_datas())


@flask_app.route("/data/innodb", methods=["GET", "POST"])
def get_innodb_status():
    return render_template("mysql_innodb.html", mysql_datas=get_mysql_datas())


@flask_app.route("/data/replication", methods=["GET", "POST"])
def get_replication_status():
    return render_template("mysql_replication.html", mysql_datas=get_mysql_datas())


@flask_app.route("/load/host_infos", methods=["GET", "POST"])
def load_all_host_info():
    cache.load_host_infos()
    return "load host info ok!"


def get_mysql_datas():
    mysql_datas = []
    obj_info = common.convert_to_object_from_post_data(request.get_data())
    if (obj_info is None or len(obj_info.host_ids) <= 0):
        return cache.get_all_mysql_datas()
    else:
        for host_id in obj_info.host_ids:
            mysql_datas.append(cache.get_mysql_data_by_host_id(host_id))
        return mysql_datas


if __name__ == '__main__':
    if (settings.LINUX_OS):
        print("linux start ok.")
        flask_app.run(debug=False, host=settings.IP, port=settings.PORT, use_reloader=False, threaded=True)
    if (settings.WINDOWS_OS):
        print("windows start ok.")
        flask_app.run(debug=True, host=settings.IP, port=settings.PORT, use_reloader=True, threaded=True)
