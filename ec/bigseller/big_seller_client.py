#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: big_seller_client
@author: jkguo
@create: 2023/8/1
"""
import json
import os
import time
import requests
from ec.verifycode.ydm_verify import YdmVerify


class BigSellerClient:

    def __init__(self, ydm_token: str):
        self.check_login_url = "https://www.bigseller.com/api/v1/index.json"
        self.login_web_url = "https://www.bigseller.com/zh_CN/login.htm"
        self.login_url = "https://www.bigseller.com/api/v2/user/login.json"
        self.gen_verify_code_url = "https://www.bigseller.com/api/v2/genVerifyCode.json"
        self.estimate_sku_url = "https://www.bigseller.com/api/v1/items/pageList.json"
        self.session = requests.Session()
        self.auto_verify_coder = YdmVerify(ydm_token)

    def login(self, email: str, encoded_password: str):
        if self.load_cookies() and self.is_login():
            print("use cookie login ok")
            return
        self.__login(email, encoded_password)

    def __login(self, email: str, encoded_password: str):
        # get login web
        self.session.get(self.login_web_url)
        # get verify code
        access_code, verify_code = self.get_valid_verify_code()
        print(f"access_code {access_code}, verify_code: {verify_code}")
        response = self.session.post(self.login_url, {
            "email": email,
            "password": encoded_password,
            "verifyCode": str(verify_code),
            "accessCode": access_code
        })
        print("login response header:")
        print(response.headers)
        print("login response json:")
        print(response.json())
        if self.is_login():
            print(f"login {email} success save cookies")
            self.save_cookies()
        else:
            raise Exception("login failed")

    def is_login(self):
        response = self.session.get(self.check_login_url).json()
        return response["data"]["user"] is not None

    def get_valid_verify_code(self):
        for i in range(10):
            response = self.session.get(self.gen_verify_code_url)
            image_base64: str = response.json()["data"]["base64Image"]
            if image_base64.startswith("data:image/png;base64,"):
                image_base64 = image_base64[len("data:image/png;base64,"):]
            # verify code
            verify_res = self.auto_verify_coder.common_verify(image_base64, "10110")
            if verify_res["code"] == 10000:
                verify_code = verify_res["data"]["data"]
                return response.json()["data"]["accessCode"], verify_code
            time.sleep(3)
        raise Exception("get_valid_verify_code failed.")

    def save_cookies(self):
        cookies_file_path = "./big_seller.cookies"
        with open(cookies_file_path, "w") as f:
            f.write(json.dumps(self.session.cookies.get_dict(), indent=2))

    def load_cookies(self):
        cookies_file_path = "./big_seller.cookies"
        if not os.path.isfile(cookies_file_path):
            return False
        with open(cookies_file_path, "r") as fp:
            self.session.cookies.update(json.load(fp))
            return True

    def load_sku_estimate_by_date(self, begin_date: str, end_date: str):
        rows = []
        page_size = 200
        page_no = 1
        while True:
            req = {
                "pageSize": page_size,
                "pageNo": page_no,
                "platform": "",
                "shopId": "",
                "searchType": "sku",
                "searchContent": "",
                "inquireType": 0,
                "beginDate": begin_date,
                "endDate": end_date,
                "orderBy": "",
                "desc": 0,
                "categoryList": ""
            }
            res = self.session.post(self.estimate_sku_url, req).json()
            total_page = res["data"]["totalPage"]
            total_size = res["data"]["totalSize"]
            print(f"load page {page_no}/{total_page} data")
            rows.extend(res["data"]["rows"])
            if total_page <= page_no:
                print(f"load all {total_size} sku")
                break
            page_no += 1
        return rows
