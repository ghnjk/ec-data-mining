#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_info_rebuild
@author: jkguo
@create: 2024/2/7
"""
from ec.sku_manager import SkuManager
from ec.sku_group_matcher import BigSellerSkuClassifier


def main():
    sc = BigSellerSkuClassifier()
    sc.load()
    sm = SkuManager()
    sm.load()
    for sku in sm.sku_map.keys():
        item = sm.sku_map[sku]
        if item["isGroup"] == 1:
            continue
        title = item["title"]
        count = item["productCount"]
        cls_name = item["classifyName"]
        cls_name = sc.get_full_class_name(cls_name)
        image_url = item["imgUrl"]
        print(f"{cls_name}\t{title}\t{sku}\t{count}\t{image_url}")


if __name__ == '__main__':
    main()
