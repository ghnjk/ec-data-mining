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


def load_all_main_sku_ids():
    main_sku_ids = []
    with open("conf/main_sku.txt", "r") as fp:
        for line in fp.readlines():
            sku = line.strip()
            if len(sku) == 0:
                continue
            main_sku_ids.append(sku)
    return main_sku_ids


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
    main_sm = SkuManager("cookies/main_sku.json")
    for sku in load_all_main_sku_ids():
        main_sm.add(client.query_sku_detail(
            sm.get_sku_id_by_sku_name(sku)
        ))
        time.sleep(0.1)
    main_sm.dump()


if __name__ == '__main__':
    main()
