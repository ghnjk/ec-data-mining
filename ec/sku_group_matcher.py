#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_group_matcher
@author: jkguo
@create: 2023/8/1
"""
import json


class SkuGroupMatcher(object):

    def __init__(self, product_label_file: str):
        self.product_groups = []
        self._load_rules(product_label_file)

    def get_product_label(self, product_name: str):
        product_name = product_name.lower()
        for label, rules  in self.product_groups:
            for r in rules:
                if product_name.find(r) >= 0:
                    return label
        print(f"UNK {product_name}")
        # exit(-1)
        return "UNKNOWN"

    def _load_rules(self, product_label_file: str):
        rows = []
        with open(product_label_file, "r") as fp:
            for line in fp.readlines():
                line = line.strip().lower()
                if len(line) == 0:
                    continue
                fields = line.split(":")
                if len(fields) != 2:
                    continue
                rows.append(
                    (fields[0].strip(), fields[1].strip())
                )
        i = 0
        while i + 1 < len(rows):
            if rows[i][0] == "label" and rows[i + 1][0] == "matches":
                fields = rows[i + 1][1].split("|")
                rules = []
                for item in fields:
                    item = item.strip().lower()
                    if len(item) == 0:
                        continue
                    rules.append(item)
                self.product_groups.append(
                    (rows[i][1], rules)
                )
            i += 2


class BigSellerSkuClassifier(object):

    def __init__(self, local_classifier_db: str = "cookies/sku_classifier.json"):
        self.local_classifier_db = local_classifier_db
        self.class_name_map: dict = {}
        self.class_id_map: dict = {}

    def add(self, item: dict):
        self.class_name_map[item["name"]] = item
        self.class_id_map[item["id"]] = item

    def get_full_class_name(self, cls_name):
        full_name = ""
        cid = self.class_name_map[cls_name]["id"]
        while cid > 1:
            item = self.class_id_map[str(cid)]
            if len(full_name) > 0:
                full_name = item["name"] + "/" + full_name
            else:
                full_name = item["name"]
            cid = item["pcid"]
        return full_name

    def dump(self):
        with open(self.local_classifier_db, "w") as fp:
            json.dump(self.class_id_map, fp, indent=2, ensure_ascii=False)

    def load(self):
        with open(self.local_classifier_db, "r") as fp:
            self.class_id_map = json.load(fp)
        for cid in self.class_id_map.keys():
            item = self.class_id_map[cid]
            self.class_name_map[item["name"]] = item
