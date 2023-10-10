#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: lazada_client
@author: jkguo
@create: 2023/10/3
"""
import json
import os
import time
import datetime
from selenium.webdriver.common.by import By
from selenium.common import WebDriverException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
import typing
from requests import Session
import requests
from ec.browser import build_chrome_driver


class LazadaClient(object):

    def __init__(self, cookie_path_prefix: str = "./lazada.cookies.",
                 path_of_driver: str = "/Users/jkguo/workspace/ec-data-mining/conf/chromedriver",
                 is_debug: bool = False):
        self.driver: typing.Optional[ChromiumDriver] = None
        self.is_debug = is_debug
        self.path_of_driver = path_of_driver
        self.cookie_path_prefix: str = cookie_path_prefix
        self.login_url = "https://sellercenter.lazada.com.ph/apps/seller/login"
        self.home_url = "https://sellercenter.lazada.com.ph/apps/home/new"
        self.session: typing.Optional[Session] = None

    def get_session(self) -> Session:
        if self.session is not None:
            return self.session
        self.session = Session()
        if self.driver is not None:
            session_c = {}
            for c in self.driver.get_cookies():
                session_c[c["name"]] = c["value"]
            self.session.cookies.update(session_c)
        return self.session

    def build_driver(self) -> ChromiumDriver:
        if self.driver is not None:
            return self.driver
        self.driver = build_chrome_driver(self.path_of_driver, self.is_debug)
        return self.driver

    def check_is_login(self, user_name: str = None) -> bool:
        s = requests.Session()
        sm = {}
        if user_name is None and self.driver is None:
            return False
        elif user_name is None:
            for c in self.build_driver().get_cookies():
                sm[c["name"]] = c["value"]
        else:
            cookie_path = f"{self.cookie_path_prefix}{user_name}.json"
            if not os.path.isfile(cookie_path):
                return False
            with open(cookie_path, "r") as fp:
                cookies = json.load(fp)
                for c in cookies:
                    sm[c["name"]] = c["value"]
        s.cookies.update(sm)
        response = s.get("https://sellercenter.lazada.com.ph/ba/sycm/lazada/dashboard/smartdiagnosis/sellers.json?_timezone=-8")
        try:
            # print(f"--- {response.text}")
            is_login = response.json()["code"] == 0
            if is_login and self.session is None:
                self.session = s
            return is_login
        except Exception:
            return False

    def login(self, user_name: str, password: str) -> bool:
        self.build_driver().get(self.login_url)
        self.driver.implicitly_wait(100)
        self.driver.find_element(By.ID, "account").send_keys(user_name)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.CLASS_NAME, "Login-password-login").submit()
        time.sleep(0.5)
        if self.__check_if_current_login():
            print(f"login {user_name} success.")
            self.save_cookies(user_name)
            return True
        else:
            return False

    def __check_if_current_login(self, check_login_mode: bool = False) -> bool:
        self.driver.implicitly_wait(0.1)
        for i in range(1000):
            error_msgs = [
                "user password mistake.",
                "Please enter a valid phone number.",
                "Incorrect username or password."
            ]
            is_error_found = False
            try:
                for div in self.driver.find_elements(By.CLASS_NAME, "next-form-item-help"):
                    # print(div.text)
                    for err in error_msgs:
                        if err in div.text or err == div.text:
                            print(f"login failed: {div.text}")
                            is_error_found = True
            except WebDriverException:
                pass
            if is_error_found:
                return False
            # check is login success
            if self.driver.current_url.startswith(self.home_url):
                try:
                    if self.driver.find_elements(By.CLASS_NAME, "profile-level"):
                        return True
                except WebDriverException:
                    pass
            if check_login_mode:
                # check if jump to login page
                if self.driver.current_url.startswith(self.login_url):
                    return False
            time.sleep(0.1)
        return False

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

    def get_all_ads_overview(self, start_ti: float, end_ti: float):
        """
        获取店铺广告汇总信息
        :return {
            "gmv": 65629, // 店铺GMV (菲律宾比索)
            "guideGmv": 45663, // 广告带来的GMV (菲律宾比索)
            "adsSpend": 6787, // 广告 花费 (菲律宾比索)
            "impressions": 曝光数
            "reachUV": // 触达的独立访客数
            "visits": // 由超级推广引导的店铺访客数
            "uniqueVisitors" // 由超级推广（含钻展、全效宝、联盟）引导进店的独立访客数
            "orders"：  // 由超级推广（含钻展、全效宝、联盟）引导的订单数
        }
        """
        start_date = datetime.datetime.fromtimestamp(start_ti).strftime("%Y%m%d")
        end_date = datetime.datetime.fromtimestamp(end_ti).strftime("%Y%m%d")
        url = f"https://sellercenter.lazada.com.ph/sponsor/solutions/data/product/storewide/overview.json?startDate={start_date}&endDate={end_date}"
        response = self.get_session().get(url).json()["result"]
        res_pkg = {
            "gmv": response["gmv"],
            "guideGmv": response["guideGmv"],
            "adsSpend": response["spend"]
        }
        url = f"https://sellercenter.lazada.com.ph/sponsor/solutions/data/product/lss.json?startDate={start_date}&endDate={end_date}&sellerId=0"
        response = self.get_session().get(url).json()["result"]
        res_pkg["impressions"] = response["totalImpressions"]
        res_pkg["reachUV"] = response["totalReachUV"]
        res_pkg["orders"] = response["totalOrders"]
        res_pkg["visits"] = response["totalVisits"]
        res_pkg["uniqueVisitors"] = response["totalUniqueVisitors"]
        return res_pkg

    def get_ads_statics(self, ads_type: str, start_ti: float, end_ti: float):
        """
        获取广告汇总信息
        :param ads_type:
        :param start_ti:
        :param end_ti:
        :return: {
            "ads_type": ads_type,
            "ads_spend": 广告花费
            "revenue": 店铺收入
            "impressions": 曝光数
            "clicks": 点击量
            "unitsSold": 店铺销售件数
        }
        """
        start_date = datetime.datetime.fromtimestamp(start_ti).strftime("%Y-%m-%d")
        end_date = datetime.datetime.fromtimestamp(end_ti).strftime("%Y-%m-%d")
        pre_s = datetime.datetime.fromtimestamp(start_ti - 24 * 3600).strftime("%Y-%m-%d")
        pre_e = datetime.datetime.fromtimestamp(end_ti - 24 * 3600).strftime("%Y-%m-%d")
        if ads_type == "全效宝":
            url = f"https://sellercenter.lazada.com.ph/sponsor/solutions/performance/report/overview.json?useRtTable=0&startDate={start_date}&endDate={end_date}&lastStartDate={pre_s}&lastEndDate={pre_e}"
            response = self.get_session().get(url)
            response = response.json()["result"]["reportOverview"]
            return {
                "ads_type": ads_type,
                "ads_spend": response["spend"],
                "revenue": response["revenue"],
                "impressions": response["impressions"],
                "clicks": response["clicks"],
                "unitsSold": response["unitsSold"]
            }
        elif ads_type == "超级联盟":
            url_path = f"/sponsor/solutions/affiliate/report/metric/overview.json?dateType=7&startDateStr={start_date}&endDateStr={end_date}"
            url = f"https://sellercenter.lazada.com.ph{url_path}"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://sellercenter.lazada.com.ph//sponsor/solutions/affiliate/report/metric/overview.json/_____tmd_____/punish?x5secdata=xcuSQPKcti291We9%2fPtkMrEXi871aXgEfK7APP9Mc%2f%2fNmeFxSLuWdWcbpnmWtt3xoGF0lN6cAt9Vw6vdDFVUMVm91Ya3Bylyvq16hF7ssdJO9v12oFKo5nUvdotAoX7Wy0NWHzrRzZ93NMtQ%2bfi6d76O8KaNcdcN%2f8b%2b4PVVyBIbOnnvli%2bmkES0mXI768DPsyg%2bbtneWdq%2b0J2gxuBlltZ5iIRm8u9chtq4NSSVyq%2bn38CFra5KevUvxKmjC3d9A62ifq%2bhk6JvgBQ%2fvgqySUk0D8400sUwFotTYvF5BlMiY%3d__bx__sellercenter.lazada.com.ph%2fsponsor%2fsolutions%2faffiliate%2freport%2fmetric%2foverview.json&x5step=1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            }
            response = self.get_session().get(url, headers=headers)
            try:
                response = response.json()["module"]
            except Exception:
                # 需要人工验证和登陆
                self.load_cookies("09771708907")
                self.build_driver().get(url)
                self.driver.implicitly_wait(100)
                self.driver.find_element(By.TAG_NAME, "pre")
                self.save_cookies("09771708907-new")
                self.session = None
                response = self.get_session().get(url)
                print(response.text)
                time.sleep(1000)
                response = response.json()["module"]
            return {
                "ads_type": ads_type,
                "ads_spend": response["mktSpend"]["value"],
                "revenue": response["mktRevenue"]["value"],
                "impressions": 0,
                "clicks": 0,
                "unitsSold": response["mktUnitsSold"]["value"]
            }
        else:
            raise Exception("unsupport ads " + ads_type)

    def quit(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None


if __name__ == '__main__':
    client = LazadaClient(is_debug=True)
    if not client.check_is_login(user_name="09451737990"):
        if client.login("09451737990", "0427107606jenny"):
            print("login success.")
        else:
            print("login failed.")
            exit(-1)
    else:
        print("already login.")
    ti = time.time() - 24 * 3600 * 3
    res = client.get_all_ads_overview(ti, ti)
    print("get_all_ads_overview")
    print(res)
