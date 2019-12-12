# -*- coding: utf-8 -*-
import time
from selenium import webdriver
import requests


class User:
    nickname = ""   # 网名
    uin = ""   # qq号
    join_time = ""  # 入群时间

    def __str__(self):
        return "\t".join(["网名: " + self.nickname, "qq号 " + str(self.uin), "入群时间: " + self.join_time]) + "\n"


class Group:
    name = ""  # 群名称
    count = 0  # 群总数
    id = ""  # 群号
    members = []  # 群友信息

    def __str__(self):
        return "群名: " + self.name + "\t人数: " + str(self.count)


class QQGroupSpider(object):
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.cookies = None
        self.headers = {
            "referer": "https://qun.qq.com/member.html",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
        }
        self.bkn = None

    group_api = "http://qun.qq.com/cgi-bin/qun_mgr/search_group_members"

    def _get_cookie(self):
        return {i['name']: i["value"] for i in self.browser.get_cookies()}

    @staticmethod
    def int_overflow(val):
        maxint = 2147483647
        if not -maxint - 1 <= val <= maxint:
            val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        return val

    def _get_bkn(self, skey):
        hash = 5381
        for i in range(len(skey)):
            hash += self.int_overflow(hash << 5) + ord(skey[i])
        return hash & 2147483647

    def get_group_members(self, group, st=0, end=20):
        data = {"gc": group.id,
                "st": str(st),
                "end": str(end),
                "sort": "0",
                "bkn": self.bkn}

        r = requests.post(self.group_api, headers=self.headers,
                          cookies=self.cookies, data=data)
        json_data = r.json()
        if not group.count:
            group.count = json_data.get("count")
        for i in json_data.get("mems", []):
            join_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i.get("join_time")))
            user = User()
            user.nickname = i.get("nick")
            user.uin = i.get("uin")
            user.join_time = join_time
            group.members.append(user)
        if st + 21 < json_data["search_count"]:
            next_start = st + 21
            end = next_start + 20
            self.get_group_members(group, next_start, end)
        time.sleep(0.5)  # 限制速度 防止被封ip

    def get_all_group(self, group_list):
        skey = self.cookies.get("skey")
        self.bkn = self._get_bkn(skey)
        for gid in group_list.keys():
            group = Group()
            group.id = gid
            group.name = group_list[gid]
            self.get_group_members(group)
            print("{} 一共有{}个群成员".format(group.name, group.count))
            with open(group.name+'.txt', "a", encoding="utf-8") as f:
                f.write("一共有{}个群成员\n".format(group.count))
                for i in group.members:
                    f.write(str(i))
                f.flush()

    def run(self):
        self.browser.get("http://qun.qq.com/member.html")
        input("登陆完成后,按任意键继续")
        self.cookies = self._get_cookie()
        if not self.cookies.get("skey"):
            print("尚未登录成功, 请重新尝试")
            self.browser.close()
            self.browser.quit()
            return
        groups = self.browser.find_elements_by_xpath("//li[@data-id]")
        group_list = {group.get_attribute("data-id"): group.get_attribute("title") for group in groups}
        self.browser.close()
        self.browser.quit()
        if len(group_list) == 0:
            print("没有任何群")
        else:
            self.get_all_group(group_list)


if __name__ == "__main__":
    spider = QQGroupSpider()
    spider.run()
