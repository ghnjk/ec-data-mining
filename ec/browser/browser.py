#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: browser
@author: jkguo
@create: 2023/10/5
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.webdriver import ChromiumDriver


def build_chrome_driver(path_of_driver: str, is_debug: bool) -> ChromiumDriver:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if not is_debug:
        options.add_argument("headless")
    driver = webdriver.Chrome(service=Service(path_of_driver), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
    })
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    if is_debug:
        driver.maximize_window()
    return driver
