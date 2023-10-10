#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: shoppee_client
@author: jkguo
@create: 2023/10/5
"""
import time
import typing
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from ec.browser import build_chrome_driver
from selenium.webdriver.common.by import By
import json
import os


class ShoppeeClient(object):

    def __init__(self, cookie_path_prefix: str = "./shoppee.cookies.",
                 path_of_driver: str = "/Users/jkguo/workspace/ec-data-mining/conf/chromedriver",
                 is_debug: bool = False):
        self.driver: typing.Optional[ChromiumDriver] = None
        self.is_debug = is_debug
        self.path_of_driver = path_of_driver
        self.cookie_path_prefix: str = cookie_path_prefix
        self.login_url = "https://shopee.ph/seller/login"
        self.home_url = "https://sellercenter.lazada.com.ph/apps/home/new"

    def login(self, user_name: str, password: str):
        self.load_cookies(user_name)
        self.build_driver().get(self.login_url)
        self.driver.implicitly_wait(100)
        self.driver.find_element(By.NAME, "loginKey").send_keys(user_name)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "form").submit()
        while True:
            time.sleep(1)
            self.save_cookies(user_name)

    def build_driver(self) -> ChromiumDriver:
        if self.driver is not None:
            return self.driver
        self.driver = build_chrome_driver(self.path_of_driver, self.is_debug)
        return self.driver

    def save_cookies(self, user_name: str):
        cookie_path = f"{self.cookie_path_prefix}{user_name}.json"
        print(f"saving cookies to file {cookie_path}")
        with open(cookie_path, "w") as fp:
            json.dump(self.driver.get_cookies(), fp, indent=2)

    def load_cookies(self, user_name: str):
        cookie_path = f"{self.cookie_path_prefix}{user_name}.json"
        if not os.path.isfile(cookie_path):
            return
        self.build_driver().get(self.login_url)
        with open(cookie_path, "r") as fp:
            cookies = json.load(fp)
            for c in cookies:
                self.build_driver().add_cookie(c)


if __name__ == '__main__':
    client = ShoppeeClient(is_debug=True)
    client.login("09179988900", "0427107606Jenny")
