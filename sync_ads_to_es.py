#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_ads_to_es
@author: jkguo
@create: 2023/10/5
"""
import time
import datetime
import typing

from ec.lazada.lazada_client import LazadaClient
import pandas as pd
from elasticsearch import Elasticsearch
from ec import app_config
from ec.shop_manager import ShopManager


def sync_ads_to_es(client: LazadaClient, es: Elasticsearch,
                   shop_manager: ShopManager, shop_info: dict, date_ti: float):
    row = client.get_all_ads_overview(date_ti, date_ti)
    shop_owner = shop_manager.get_shop_owner(shop_info["shop_name"])
    if shop_owner == "UNKNOWN":
        print("UNK SHOP: " + shop_info["shop_name"])
        exit(-1)
    sync_date = datetime.datetime.fromtimestamp(date_ti).strftime("%Y-%m-%d")
    row.update({
        "time": sync_date,
        "docId": f"{sync_date}-{shop_info['shop_plat']}-{shop_info['shop_phone']}",
        "platform": shop_info["shop_plat"],
        "shopName": shop_info["shop_name"],
        "shopOwner": shop_owner
    })
    es.index(index="ec_ads_overview", id=row["docId"], body=row)


def parse_shop_info(row)-> typing.Optional[dict]:
    plat = row["平台"]
    if plat != "lazada":
        return None
    shop_name = row["店名"].strip()
    shop_phone = row["注册手机号"].strip()
    shop_passwd = row["密码"].strip()
    shop_owner = row["运营人员"].strip()
    shop_info = {
        "shop_plat": plat,
        "shop_name": shop_name,
        "shop_phone": shop_phone,
        "shop_passwd": shop_passwd,
        "shop_owner": shop_owner
    }
    if shop_name == "" or shop_phone == "" or shop_passwd == "" or shop_owner == "":
        print(f"ERROR: invalid shop info for row {row}")
        exit(-1)
    print(f"parse shop info: shop {plat}/{shop_name} phone {shop_phone} passwd {shop_passwd} owner {shop_owner}")
    return shop_info


def main():
    conf = app_config.get_app_config()
    shop_manager = ShopManager(app_config.get_config_file("shop_info.txt"))
    es = Elasticsearch(conf["es_hosts"], http_auth=(conf["es_user"], conf["es_passwd"]))
    df = pd.read_excel("conf/all_shops.xlsx", "shops",
                       dtype={
                           "注册手机号": "str",
                           "密码": "str"
                       })
    for idx, row in df.iterrows():
        shop_info = parse_shop_info(row)
        if shop_info is None:
            continue
        client = LazadaClient(cookie_path_prefix="cookies/lazada.cookies.", is_debug=True)
        if not client.check_is_login(user_name=shop_info["shop_phone"]):
            if client.login(shop_info["shop_phone"], shop_info["shop_passwd"]):
                print(f"login {shop_info['shop_phone']} success.")
            else:
                print(f"login {shop_info['shop_phone']} failed.")
                exit(-1)
        else:
            print(f"account {shop_info['shop_phone']} use local cookies.")

        now = time.time()
        for i in range(7):
            ti = now - (i + 1) * 24 * 3600
            date = datetime.datetime.fromtimestamp(ti).strftime("%Y-%m-%d")
            print(f"shop {shop_info['shop_plat']}/{shop_info['shop_name']} sync {date} ...")
            sync_ads_to_es(client, es, shop_manager, shop_info, ti)

        client.quit()


if __name__ == '__main__':
    main()
