#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: ydm_verify
@author: jkguo
@create: 2023/8/1
"""
import json
import time
import requests
import base64


class YdmVerify(object):

    def __init__(self, token: str):
        self._custom_url = "http://api.jfbym.com/api/YmServer/customApi"
        self._token = token
        self._headers = {
            'Content-Type': 'application/json'
        }

    def common_verify(self, image_base64_str: str, verify_type="60000"):
        # 数英汉字类型
        # 通用数英1-4位 10110
        # 通用数英5-8位 10111
        # 通用数英9~11位 10112
        # 通用数英12位及以上 10113
        # 通用数英1~6位plus 10103
        # 定制-数英5位~qcs 9001
        # 定制-纯数字4位 193
        # 中文类型
        # 通用中文字符1~2位 10114
        # 通用中文字符 3~5位 10115
        # 通用中文字符6~8位 10116
        # 通用中文字符9位及以上 10117
        # 定制-XX西游苦行中文字符 10107
        # 计算类型
        # 通用数字计算题 50100
        # 通用中文计算题 50101
        # 定制-计算题 cni 452
        payload = {
            "image": image_base64_str,
            "token": self._token,
            "type": verify_type
        }
        print(payload)
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()

    def slide_verify(self, slide_image, background_image, verify_type="20101"):
        # 滑块类型
        # 通用双图滑块  20111
        payload = {
            "slide_image": base64.b64encode(slide_image).decode(),
            "background_image": base64.b64encode(background_image).decode(),
            "token": self._token,
            "type": verify_type
        }
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def sin_slide_verify(self, image, verify_type="20110"):
        # 通用单图滑块(截图)  20110
        payload = {
            "image": base64.b64encode(image).decode(),
            "token": self._token,
            "type": verify_type
        }
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def traffic_slide_verify(self, seed, data, href, verify_type="900010"):
        # 定制-滑块协议slide_traffic  900010
        payload = {
            "seed": seed,
            "data": data,
            "href": href,
            "token": self._token,
            "type": verify_type
        }
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def click_verify(self, image, label_image=None, extra=None, verify_type="30100"):
        # 通用任意点选1~4个坐标 30009
        # 通用文字点选1(extra,点选文字逗号隔开,原图) 30100
        # 定制-文字点选2(extra="click",原图) 30103
        # 定制-单图文字点选 30102
        # 定制-图标点选1(原图) 30104
        # 定制-图标点选2(原图,extra="icon") 30105
        # 定制-语序点选1(原图,extra="phrase") 30106
        # 定制-语序点选2(原图) 30107
        # 定制-空间推理点选1(原图,extra="请点击xxx") 30109
        # 定制-空间推理点选1(原图,extra="请_点击_小尺寸绿色物体。") 30110
        # 定制-tx空间点选(extra="请点击侧对着你的字母") 50009
        # 定制-tt_空间点选 30101
        # 定制-推理拼图1(原图,extra="交换2个图块") 30108
        # 定制-xy4九宫格点选(原图,label_image,image) 30008
        payload = {
            "image": base64.b64encode(image).decode(),
            # "label_image": base64.b64encode(label_image).decode(),
            "token": self._token,
            "type": verify_type
        }
        if extra:
            payload['extra'] = extra
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def rotate(self, out_ring_image, inner_circle_image):
        # 定制-X度单图旋转  90007
        # payload = {
        #     "image": base64.b64encode(image).decode(),
        #     "token": self._token,
        #     "type": "90007"
        # }
        # 定制-Tt双图旋转,2张图,内圈图,外圈图  90004
        payload = {
            "out_ring_image": base64.b64encode(out_ring_image).decode(),
            "inner_circle_image": base64.b64encode(inner_circle_image).decode(),
            "token": self._token,
            "type": "90004"
        }
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def google_verify(self, googlekey, pageurl, invisible=1, data_s=""):
        _headers = {
            'Content-Type': 'application/json'
        }
        """
        第一步，创建验证码任务
        :param
        :return taskId : string 创建成功的任务ID
        """
        url = "http://122.9.52.147/api/YmServer/funnelApi"
        payload = json.dumps({
            "token": self._token,
            # "type": "40011", ## v3
            "type": "40010",  ## v2
            "googlekey": googlekey,
            "enterprise": 1,  ## 是否为企业版
            "pageurl": pageurl,
            "invisible": invisible,
            "data-s": data_s,
            # 'action':"TEMPLATE" #V3必传
        })
        # 发送JSON格式的数据
        result = requests.request("POST", url, headers=_headers, data=payload).json()
        print(result)
        # {'msg': '识别成功', 'code': 10000, 'data': {'code': 0, 'captchaId': '51436618130', 'recordId': '74892'}}
        captcha_id = result.get('data').get("captchaId")
        record_id = result.get('data').get("recordId")
        times = 0
        while times < 150:
            try:
                url = f"http://122.9.52.147/api/YmServer/funnelApiResult"
                data = {
                    "token": self._token,
                    "captchaId": captcha_id,
                    "recordId": record_id
                }
                result = requests.post(url, headers=_headers, json=data).json()
                print(result)
                # {'msg': '结果准备中，请稍后再试', 'code': 10009, 'data': []}
                if result['msg'] == "结果准备中，请稍后再试":
                    time.sleep(5)
                    times += 5
                    continue
                if result['msg'] == '请求成功' and result['code'] == 10001:
                    print(result['data']['data'])
                    return result['data']['data']
                    # {'msg': '请求成功', 'code': 10001, 'data': {'data': '03AGdBq2611GTOgA2v9HUpMMEUE70p6dwOtYyHJQK4xhdKF0Y8ouSGsFZt647SpJvZ22qinYrm6MYBJGFQxMUIApFfSBN6WTGspk6DmFdQAoWxynObRGV7qNMQOjZ_m4w3_6iRu8SJ3vSUXH_HHuA7wXARJbKEpU4J4R921NfpKdahgeFD8rK1CFYAqLd5fz4l-8_VRmRE83dRSfkgyTN338evQ1doWKJRipZbk4ie-89Ud0KGdOsP4QzG3stRZgj2oaEoMDSAP62vxKGYqtDEqTcwtlgo-ot3rF5SmntaoKGwcKPo0NrekWA5gtj0vqKLU6lY2GcnSci_tgBzBwuH40uvyR1PFu02VK_E44mopJ7FOO4cUukNaLGqypU2YCA8QuaaebOIoCMU7RGqGs_41RYNCG1GSdthiwcwk2hHFbi-TXuICXSwh4Er5mgVW9A3t_9Ndp0eJcyr3HtuJrcA7BtlcgruuQxK5h4Ew4ert4KPH_aQGN9ww5VsUtbSManzUDnUOs7aEdvFk1DOOPmLys-aX20ZFN2CcQcZZSO-7HZpZZt3EDeWWE5S02HFDY8gl3_0xqIts8774Tr4GMVJaddG0NR6pcBFC11FqNcK2a18gM3gaKDy3_2ZMeSU4nj4NWwoAhPjQN2BS8JxX4kKVpX4rD959kc93vczVD3TYD6_4GJahGSpBvM7Y5_GGIdLL8imXde1R35mZnEcFYXQ40zcy3DdJFkk_gzGTVOEb1Q1IZpjMxzCxyGgwjgL9dtDIgst5H5CSZoerX_Lz-DmsBvYIYZdpbPLEMROx9MODImaEw8Cp6M8Xj7_foijiGE9hh-pzJSTlKl3HytiSUyJJ7r1BssrX5C_TFWxl0IXNg8azP8H-ZIOWwnYlMWCS1w9piHdoLg5zACiYIN3Txdlsvi61MuPmzJggJd1_dlyMdAlzb5_zdfweqj0_Ko1ODP378YT7sV7LECgRj5QJU6sF5nlf4m2g5sFypBw9GFAkEE-OaWGYxRJOy2ioU41ggAJIkcza2B_N5AL2KLROtm0-c2MxplM4ZzHxrUv9A24zlgzo3Pz4NONwU_gaOcDB7j1dZKXD8UaoIrZv0BTd8JeojYowm9Usdg7Rt4Fpo_vDLJdrEUfbxVlXieDD9Fr1fu72-d4AduT_J3n-rIhyX4gFav-KfP-qOxqOZsmjXZirsBxZs7042NYeirRYnLv35cxIAJARz03FJmeKViUivwC5mCWw64hjRad9XyyBOP2n8KFOrTXhPskC-WwEfksGtfLxi6VW76FHGvRdwHXzMwVfNqe3P5H_WZUc-vxeTAsTnqZz3WA97lM4MLrX0nTZYgXxCEiS6raSOiEMqcx_Nv7Zxre-abj4LZRbFpH8nx1SEiaOV2Dm-a1iPFEmCs0L4kDtt6VImSVIQaTOAd3KFSo7W_XTvRPsQJOtblrcKyuagztX_Yr0lT0YqN9I9MZAARo7M5OfwSLJW16rdmp4NuRefEvNPNHO2cVh1Xha1qNGuF_QDvWFFmWG0Y6IbRqLmF-Dv8BY4TWyOeVnADJftGQw2QSr8RmbCHryA'}}
            except Exception as e:
                print(e)
                continue

    def fun_captcha_verify(self, publickey, pageurl, verify_type="40007"):
        # 定制类接口-Hcaptcha 40007
        payload = {
            "publickey": publickey,
            "pageurl": pageurl,
            "token": self._token,
            "type": verify_type
        }
        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        print(resp.text)
        return resp.json()['data']['data']

    def hcaptcha_verify(self):
        # 定制类接口-Hcaptcha
        _headers = {
            'Content-Type': 'application/json'
        }
        _custom_url = "http://api.jfbym.com/api/YmServer/funnelApi"
        payload = {
            "sitekey": "",
            "pageurl": "",
            "token": self._token,
            "type": '50013'
        }
        result = requests.post(_custom_url, headers=_headers, data=json.dumps(payload)).json()
        print(result)
        captcha_id = result.get('data').get("captchaId")
        record_id = result.get('data').get("recordId")
        times = 0
        while times < 150:
            try:
                url = f"http://api.jfbym.com/api/YmServer/funnelApiResult"
                data = {
                    "token": self._token,
                    "captchaId": captcha_id,
                    "recordId": record_id
                }
                result = requests.post(url, headers=_headers, json=data).json()
                print(result)
                # {'msg': '结果准备中，请稍后再试', 'code': 10009, 'data': []}
                if result['msg'] == "结果准备中，请稍后再试":
                    time.sleep(5)
                    times += 5
                    continue
                if result['msg'] == '请求成功' and result['code'] == 10001:
                    print(result['data']['data'])
                    return result['data']['data']
                    # {'msg': '请求成功', 'code': 10001, 'data': {'data': '03AGdBq2611GTOgA2v9HUpMMEUE70p6dwOtYyHJQK4xhdKF0Y8ouSGsFZt647SpJvZ22qinYrm6MYBJGFQxMUIApFfSBN6WTGspk6DmFdQAoWxynObRGV7qNMQOjZ_m4w3_6iRu8SJ3vSUXH_HHuA7wXARJbKEpU4J4R921NfpKdahgeFD8rK1CFYAqLd5fz4l-8_VRmRE83dRSfkgyTN338evQ1doWKJRipZbk4ie-89Ud0KGdOsP4QzG3stRZgj2oaEoMDSAP62vxKGYqtDEqTcwtlgo-ot3rF5SmntaoKGwcKPo0NrekWA5gtj0vqKLU6lY2GcnSci_tgBzBwuH40uvyR1PFu02VK_E44mopJ7FOO4cUukNaLGqypU2YCA8QuaaebOIoCMU7RGqGs_41RYNCG1GSdthiwcwk2hHFbi-TXuICXSwh4Er5mgVW9A3t_9Ndp0eJcyr3HtuJrcA7BtlcgruuQxK5h4Ew4ert4KPH_aQGN9ww5VsUtbSManzUDnUOs7aEdvFk1DOOPmLys-aX20ZFN2CcQcZZSO-7HZpZZt3EDeWWE5S02HFDY8gl3_0xqIts8774Tr4GMVJaddG0NR6pcBFC11FqNcK2a18gM3gaKDy3_2ZMeSU4nj4NWwoAhPjQN2BS8JxX4kKVpX4rD959kc93vczVD3TYD6_4GJahGSpBvM7Y5_GGIdLL8imXde1R35mZnEcFYXQ40zcy3DdJFkk_gzGTVOEb1Q1IZpjMxzCxyGgwjgL9dtDIgst5H5CSZoerX_Lz-DmsBvYIYZdpbPLEMROx9MODImaEw8Cp6M8Xj7_foijiGE9hh-pzJSTlKl3HytiSUyJJ7r1BssrX5C_TFWxl0IXNg8azP8H-ZIOWwnYlMWCS1w9piHdoLg5zACiYIN3Txdlsvi61MuPmzJggJd1_dlyMdAlzb5_zdfweqj0_Ko1ODP378YT7sV7LECgRj5QJU6sF5nlf4m2g5sFypBw9GFAkEE-OaWGYxRJOy2ioU41ggAJIkcza2B_N5AL2KLROtm0-c2MxplM4ZzHxrUv9A24zlgzo3Pz4NONwU_gaOcDB7j1dZKXD8UaoIrZv0BTd8JeojYowm9Usdg7Rt4Fpo_vDLJdrEUfbxVlXieDD9Fr1fu72-d4AduT_J3n-rIhyX4gFav-KfP-qOxqOZsmjXZirsBxZs7042NYeirRYnLv35cxIAJARz03FJmeKViUivwC5mCWw64hjRad9XyyBOP2n8KFOrTXhPskC-WwEfksGtfLxi6VW76FHGvRdwHXzMwVfNqe3P5H_WZUc-vxeTAsTnqZz3WA97lM4MLrX0nTZYgXxCEiS6raSOiEMqcx_Nv7Zxre-abj4LZRbFpH8nx1SEiaOV2Dm-a1iPFEmCs0L4kDtt6VImSVIQaTOAd3KFSo7W_XTvRPsQJOtblrcKyuagztX_Yr0lT0YqN9I9MZAARo7M5OfwSLJW16rdmp4NuRefEvNPNHO2cVh1Xha1qNGuF_QDvWFFmWG0Y6IbRqLmF-Dv8BY4TWyOeVnADJftGQw2QSr8RmbCHryA'}}
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    ydm = YdmVerify("xxxx")
    image = "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"
    response = ydm.common_verify(image, "10110")
    # {"msg":"识别成功","code":10000,"data":{"code":0,"data":"ktmw","time":0.012674093246459961,"unique_code":"21ec190860f88d81500dd54366a120dd"}}
    print(response)
