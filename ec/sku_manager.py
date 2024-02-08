#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_manager
@author: jkguo
@create: 2024/2/7
"""
import json
import typing


class SkuManager(object):

    def __init__(self, local_db_path: str = "cookies/all_sku.json"):
        self.local_db_path = local_db_path
        # sku_map = dict[sku_name, sku_info]
        self.sku_map: dict = {}

    def add(self, sku: dict):
        key = sku["sku"]
        if key in self.sku_map:
            raise f"conflict sku {key}"
        self.sku_map[key] = sku

    def dump(self):
        with open(self.local_db_path, "w") as fp:
            json.dump(self.sku_map, fp, indent=2, ensure_ascii=False)

    def load(self):
        with open(self.local_db_path, "r") as fp:
            self.sku_map = json.load(fp)

    def get_sku_id_by_sku_name(self, sku_name: str) -> typing.Optional[int]:
        item = self.sku_map.get(sku_name)
        if item is None:
            return None
        return item["id"]
