from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 
import os
import requests
import time
import random
import psycopg2

debug_flag = False

headers = {
    "Authorization": "Bearer " + "BMdyXN54oSPziBSoypnpXf3tKkiq3k7SeomOvdFKz80",
    "Content-Type": "application/x-www-form-urlencoded"
}

url = "https://sports.tms.gov.tw/venues/?K=49#Schedule"
elements_id = dict()


class PostgresBaseManager:

    def __init__(self):

        self.database = 'd4huo08q01ibjl'
        self.user = 'xgaurqsmfgazfi'
        self.password = '1008e263088ac516f659d9e0eada575bec6b0c4acffa5279b36806664a43165b'
        self.host = 'ec2-52-45-238-24.compute-1.amazonaws.com'
        self.port = '5432'
        self.conn = self.connectServerPostgresDb()

    def connectServerPostgresDb(self):
        """
        :return: 連接 Heroku Postgres SQL 認證用
        """
        conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)
        return conn

    def closePostgresConnection(self):
        """
        :return: 關閉資料庫連線使用
        """
        self.conn.close()

    def runServerPostgresDb(self):
        """
        :return: 測試是否可以連線到 Heroku Postgres SQL
        """
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM taipeigym')
        results = cur.fetchall()
        global elements_id
        elements_id = {x.strip(): y.strip() for (x,y) in results}
        self.conn.commit()
        cur.close()


def send_line_notification(params):
    r = requests.post("https://notify-api.line.me/api/notify",
                          headers=headers, params=params)


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_availability(driver):
    driver.get(url)
    
    trial_count = 10
    while (check_exists_by_xpath(driver, '//*[@id="PickupDateInterFaceBox"]') is not True and trial_count > 0):
        trial_count -= 1
        time.sleep(3)
    
    try:
        target = driver.find_element_by_xpath('//*[@id="PickupDateInterFaceBox"]')
    except NoSuchElementException:
        params = {"message": f"!!! 程式發生錯誤! 請檢察系統"}
        send_line_notification(params)


    action = ActionChains(driver)
    action.move_to_element(target).perform()
    time.sleep(1)
    for _ in range(8):
        driver.execute_script("arguments[0].scrollBy(900,0)", target);
        time.sleep(1)
    
    time.sleep(1)
    
    for i in elements_id:
        trial_count = 10
        while (check_exists_by_xpath(driver, f"//*[@id='Sched.{elements_id[i]}']") is not True and trial_count > 0):
            trial_count -= 1
            time.sleep(3)

        try:
            l = driver.find_element_by_xpath(f"//*[@id='Sched.{elements_id[i]}']")
            print(f"Value: {l.text}")
        except NoSuchElementException:
            params = {"message": f"!!! 程式發生錯誤! 請檢察系統"}
            send_line_notification(params)

        print(f"Checking {i} if it startswith {i[11:13]}")
        if l.text.startswith(i[11:13]):
            params = {"message": f"‼️‼️ 我找到 {i} {l.text} 有開放 趕快去訂 ‼️‼️"}
            send_line_notification(params)
        elif l.text.startswith("零租"):
            params = {"message": f"😣 已經被搶走了 時間:{i} 顯示為{l.text} "}
            send_line_notification(params)
        else:
            if debug_flag or random.randint(0,101) == 10:
                params = {"message": f"*** 😀 自動檢查 台北體育館 {i} 沒有開放. 原因: {l.text}"}
                send_line_notification(params)


if __name__ == '__main__':
    postgres_manager = PostgresBaseManager()
    postgres_manager.runServerPostgresDb()
    postgres_manager.closePostgresConnection()
    print(f"elements_id: {elements_id}")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage') 
    driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    while True:
        if random.randint(0,100) == 10:
            params = {"message": f"*** 請放心 我還在跑呦😀"}
            send_line_notification(params)

        check_availability(driver)
        time.sleep(30)

    driver.close()