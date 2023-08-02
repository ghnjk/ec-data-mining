#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: app_config
@author: jkguo
@create: 2023/8/1
"""
import json
import os


CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "conf"
)


def get_config_file(file_name: str):
    return os.path.join(CONFIG_DIR, file_name)


def get_app_config():
    with open(get_config_file("application.json"), "r") as fp:
        return json.load(fp)
