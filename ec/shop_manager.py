#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: shop_manager
@author: jkguo
@create: 2023/8/1
"""


class ShopManager(object):

    def __init__(self, shop_info_file: str):
        self.shops = {}
        self.__load_shop_info(shop_info_file)

    def get_shop_owner(self, shop_name: str):
        if shop_name not in self.shops.keys():
            print(f"UNKNOWN SHOP {shop_name}")
        return self.shops.get(shop_name, "UNKNOWN")

    def __load_shop_info(self, shop_info_file: str):
        with open(shop_info_file, "r") as fp:
            for line in fp.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                fields = line.split("|")
                if len(fields) != 2:
                    continue
                shop_name = fields[0].strip()
                owner = fields[1].strip()
                self.shops[shop_name] = owner
