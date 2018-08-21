import requests
import sqlite3
import os
import sys
from bs4 import BeautifulSoup

SendKey = ""
base_url = "http://jwc.seu.edu.cn"

if SendKey == "":
    print("请到 Server酱 申请一对多推送 SendKey")
    sys.exit(0)

conn = sqlite3.connect("record.db")
c = conn.cursor()
try:
    c.execute("""CREATE TABLE News
                (id int PRIMARY KEY, title text, link text)""")
except sqlite3.OperationalError as e:
    if "already exists" in str(e):
        pass
    else:
        print(e)
        sys.exit(0)

res = requests.get(base_url)
html = res.content.decode("u8")
soup = BeautifulSoup(html, "lxml")

for i in range(5, 10):
    w = soup.find_all(id="wp_news_w{}".format(i))[0]
    w_list = w.find_all("a")
    for item in w_list:
        title = item.get_text()
        link = base_url + item.get("href")
        c.execute("SELECT * FROM News WHERE title=?", (title,))
        data = c.fetchall()
        if len(data) == 0:
            c.execute("INSERT INTO News VALUES (NULL, ?, ?)", (item.get_text(), item.get("href")))
            payload = {"sendkey": SendKey, "text": title, "desp": "[查看原文]({})".format(link)}
            res = requests.get("https://pushbear.ftqq.com/sub", params=payload)

conn.commit()
conn.close()
