import json
import os
import random
import time
from datetime import datetime

import requests as requests
import urllib3


class Examer:
    # 考试信息
    __exam = {"id": 0,
              "title": ""}
    # 考生信息
    __user = {"name": "",
              "id": ""}

    __proxies = {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}

    __urls = {"paper": "https://dj.hbisco.com/api/jykaoshi/getShijuanById",
              "list": "https://dj.hbisco.com/api/jykaoshirenyuan/listByKsIdAndSfzh",
              "start": "https://dj.hbisco.com/api/jykaoshirenyuan/start",
              "finish": "https://dj.hbisco.com/api/jykaoshirenyuan/finish"}

    __headers = {
        "Host": "dj.hbisco.com",
        "Connection": "close",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
                      "like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://dj.hbisco.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://dj.hbisco.com/mobile/zhuanti/yzyh20210413/ksTongyong.html?id=" + str(__exam["id"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    __session = requests.session()
    __session.verify = False
    # __session.proxies = __proxies
    __session.headers = __headers

    def __init__(self, user_name: str, user_id: str, exam_id: int, exam_title: str):
        """
        构造函数
        :param user_name: 姓名
        :param user_id: 身份证号
        :param exam_id: 考试编号
        :param exam_title: 考试标题
        """
        self.__user["name"] = user_name
        self.__user["id"] = user_id
        self.__exam["id"] = exam_id
        self.__exam["title"] = exam_title

    def get_exam_paper(self):
        """
        获取考试试卷
        :return: 试卷json
        """
        try:
            # 需要发送的数据
            payload = {"id": self.__exam["id"]}
            # 禁用安全请求警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # 提交请求并返回JSON
            response = self.__session.post(self.__urls["paper"], data=payload)
            response.raise_for_status()
            result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            print('请求试卷错误:', e)
        return None

    def get_exam_times(self) -> int:
        """
        获取考试次数
        :return: 考试次数
        """
        try:
            # 需要发送的数据
            payload = {"ksId": self.__exam["id"],
                       "sfzh": self.__user["id"]}
            # 禁用安全请求警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # 提交请求
            response = self.__session.post(self.__urls["list"], data=payload)
            response.raise_for_status()
            result = response.json()
            return len(result)

        except requests.exceptions.RequestException as e:
            print('请求考试次数错误:', e)
        return 0

    def exam_start(self, times: int) -> int:
        try:
            # 需要发送的数据
            data = {"ksId": self.__exam["id"],
                    "name": self.__user["name"],
                    "sfzh": self.__user["id"],
                    "times": times,
                    "ksTitle": self.__exam["title"]}
            payload = ("&".join([f"{key}={value}" for key, value in data.items()])).encode("utf-8")

            # 禁用安全请求警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # 提交请求
            response = self.__session.post(self.__urls["start"], data=payload)
            response.raise_for_status()
            return int(response.text)

        except requests.exceptions.RequestException as e:
            print('请求考试开始错误:', e)
        return 0

    def exam_finish(self, times: int, paper_id: int, score: int, exam_json):
        try:
            user_json = {
                "ksId": self.__exam["id"],
                "name": self.__user["name"],
                "sfzh": self.__user["id"],
                "times": times,
                "ksTitle": self.__exam["title"],
                "id": paper_id,
                "score": score,
                "maxScore": 100,
                "state": 2
            }
            payload = {
                "kaoshiRenyuanJson": json.dumps(user_json, ensure_ascii=False, separators=(',', ':')),
                "kaoshiRenyuanResultJson": exam_json
            }
            # 禁用安全请求警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # 提交请求
            response = self.__session.post(self.__urls["finish"], data=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print('请求考试结束错误:', e)
        return None

    @staticmethod
    def convert_json(paper_id: int, json_data):
        new_json_data = []
        __now = 0
        __max = len(json_data)
        __count = 0
        for item in json_data:
            __temp = Examer.generate_random(0.7, __now, __max, __count)
            __count += 1 if __temp > 0 else 0
            __now += 1

            new_item = {
                "ksRyId": paper_id,
                "tkId": int(item["tkId"]),
                "tkTitle": item["title"],
                "tkType": item["type"],
                "answer": item["answer"],
                "isRight": __temp,
                "score": int(item["score"])
            }
            new_json_data.append(new_item)

        return json.dumps(new_json_data, ensure_ascii=False, separators=(',', ':')), (__count * 2)

    @staticmethod
    def generate_random(probability: float, now: int, __max: int, count: int) -> int:
        p = probability
        if now > 0:
            remaining = __max - now
            real_probability = count / __max
            diff_probabilit = (probability - real_probability)
            p = probability + (diff_probabilit / remaining) * 5
            # print(f"剩余次数:{remaining}, 当前概率:{real_probability:.2f}, 概率差:{diff_probabilit:.2f}, 修正概率:{p:.2f}")

        return 1 if p > random.random() else 0

    def exam(self):
        times = self.get_exam_times() + 1
        print(f"开始进行第{times}次答题!")
        exam_paper = self.get_exam_paper()
        print(f"获取考试试卷")
        paper_id = self.exam_start(times)
        print(f"开始考试,试卷号:{paper_id}")
        exam_json, score = Examer.convert_json(paper_id, exam_paper)
        print(f"转换试卷,得分:{score}")
        wait_time = random.randint(120, 300)
        print(f"等待 {wait_time} 秒后交卷")
        time.sleep(wait_time)
        print(f"准备提交试卷")
        finish_json = self.exam_finish(times, paper_id, score, exam_json)
        print(f"考试结束,保存考试数据")

        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename_paper = os.path.join(f'{current_time}_{paper_id}_paper.json')
        filename_finish = os.path.join(f'{current_time}_{score}_finish.json')
        with open(filename_paper, 'w', encoding='utf-8') as file:
            json.dump(exam_paper, file, ensure_ascii=False)
        with open(filename_finish, 'w', encoding='utf-8') as file:
            json.dump(finish_json, file, ensure_ascii=False)
