# -*- coding: utf-8 -*-
import time
from selenium import webdriver
import requests
import json


class QQGroupSpider(object):
    def __init__(self):
        self.browser = webdriver.Chrome()

    def _get_cookie(self):
        return {i['name']: i["value"] for i in self.browser.get_cookies()}

    def _get_bkn(self):
        cookies = self._get_cookie()
        skey = cookies.get("skey")
        js = "var hash = 5381;  for(var i = 0, len ='" + skey + "'.length; i < len; ++i){ hash += (hash << 5) + '" + skey + "'.charAt(i).charCodeAt();  }  return hash"
        gtk = self.browser.execute_script(js)
        bkn = gtk & 0x7fffffff
        return bkn

    def get_all_group(self, group_list):
        bkn = self._get_bkn()
        cookies = self._get_cookie()
        for gid in group_list.keys():
            data = {"gc": gid,
                    "st": "0",
                    "end": "2000",
                    "sort": "0",
                    "bkn": bkn}
            r = requests.post("http://qun.qq.com/cgi-bin/qun_mgr/search_group_members", cookies=cookies, data=data)
            json_data = json.loads(r.text)
            count = json_data.get("count")
            print("{} 一共有{}个群成员".format(group_list[gid], count))
            with open(group_list[gid]+'.txt', "a", encoding="utf-8") as f:
                f.write("一共有{}个群成员\n".format(count))
                for i in json_data.get("mems"):
                    local_time = time.localtime(i.get("join_time"))
                    join_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    f.write("{nk}----{num}----{join_time}\n".format(nk=i.get("nick"),num=i.get("uin"),join_time=join_time))

    def run(self):
        self.browser.get("http://qun.qq.com/member.html")
        input("登陆完成后,按任意键继续")
        groups = self.browser.find_elements_by_xpath("//li[@data-id]")
        group_list = {group.get_attribute("data-id"): group.get_attribute("title") for group in groups}
        if len(group_list) == 0:
            print("没有任何群")
        else:
            self.get_all_group(group_list)


if __name__ == "__main__":
    spider = QQGroupSpider()
    spider.run()
