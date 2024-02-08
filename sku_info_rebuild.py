#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_info_rebuild
@author: jkguo
@create: 2024/2/7
"""
from ec.sku_manager import SkuManager
from ec.sku_group_matcher import BigSellerSkuClassifier
from sync_sku import load_all_main_sku_ids


def main():
    sc = BigSellerSkuClassifier()
    sc.load()
    main_sm = SkuManager("cookies/main_sku.json")
    main_sm.load()
    for sku in load_all_main_sku_ids():
        item = main_sm.sku_map[sku]
        title = item["title"]
        count = 0
        for vo in item["warehouseVoList"]:
            count += vo["available"]
        cls_name = sc.get_full_class_name(item["classify"]["id"])
        image_url = item["imgUrl"]
        print(f"{cls_name}\t{title}\t{sku}\t{count}\t{image_url}")


if __name__ == '__main__':
    main()
