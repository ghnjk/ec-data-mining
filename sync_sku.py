#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_sku
@author: jkguo
@create: 2024/2/7
"""
import time
from ec.sku_manager import SkuManager
from ec.sku_group_matcher import BigSellerSkuClassifier
from ec import app_config
import datetime
from ec.bigseller.big_seller_client import BigSellerClient


def main():
    sm = SkuManager()
    conf = app_config.get_app_config()
    client = BigSellerClient(conf["ydm_token"])
    client.login(conf["big_seller_mail"], conf["big_seller_encoded_passwd"])
    for row in client.load_all_sku():
        sm.add(row)
    sm.dump()
    sc = BigSellerSkuClassifier()
    for row in client.load_all_sku_classes():
        sc.add(row)
    sc.dump()


if __name__ == '__main__':
    main()
