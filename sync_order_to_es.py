#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_order_to_es.py
@author: jkguo
@create: 2023/8/1
"""
import time

from ec import app_config
import datetime
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_group_matcher import SkuGroupMatcher
from ec.shop_manager import ShopManager
from elasticsearch import Elasticsearch


def enrich_sku_info(doc: dict, sku_matcher: SkuGroupMatcher, shop_manager: ShopManager):
    # skuGroup
    doc["skuGroup"] = sku_matcher.get_product_label(doc["productName"])
    # shopGroup
    # shopOwner
    doc["shopOwner"] = shop_manager.get_shop_owner(doc["shopName"])
    # saleAmount
    doc["saleAmount"] = int(float(doc["salesStr"]) * 100)
    # refundAmount
    doc["refundAmount"] = int(float(doc["refundsStr"]) * 100)
    # cancelsAmount
    doc["cancelsAmount"] = int(float(doc["cancelsStr"]) * 100)
    # efficientsAmount
    doc["efficientsAmount"] = int(float(doc["efficientsStr"]) * 100)
    # docId
    keys = [
        "time",
        "shopId",
        "skuId"
    ]
    doc_id = ""
    for k in keys:
        if len(doc_id) > 0:
            doc_id += "_"
        doc_id = doc_id + str(doc[k])
    doc["docId"] = doc_id


def sync_sku_orders_to_es(order_date: str):
    conf = app_config.get_app_config()
    client = BigSellerClient(conf["ydm_token"])
    client.login(conf["big_seller_mail"], conf["big_seller_encoded_passwd"])
    sku_matcher = SkuGroupMatcher(app_config.get_config_file("product_label.txt"))
    shop_manager = ShopManager(app_config.get_config_file("shop_info.txt"))
    es = Elasticsearch(conf["es_hosts"], http_auth=(conf["es_user"], conf["es_passwd"]))

    # 拉取所有的sku信息
    rows = client.load_sku_estimate_by_date(order_date, order_date)
    for r in rows:
        r["time"] = order_date
        enrich_sku_info(r, sku_matcher, shop_manager)
        es.index(index="ec_analysis_sku", id=r["docId"], body=r)


def main():
    now = time.time()
    for i in range(3):
        ti = now - (i + 1) * 24 * 3600
        date = datetime.datetime.fromtimestamp(ti).strftime("%Y-%m-%d")
        print(f"sync {date} ...")
        sync_sku_orders_to_es(date)


if __name__ == '__main__':
    main()
