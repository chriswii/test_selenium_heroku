from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import time
import random

debug_flag = False

headers = {
    "Authorization": "Bearer " + "BMdyXN54oSPziBSoypnpXf3tKkiq3k7SeomOvdFKz80",
    "Content-Type": "application/x-www-form-urlencoded"
}

url = "https://sports.tms.gov.tw/venues/?K=49#Schedule"
elements_id = {"2021-10-02 10 am":"10497834", "2021-10-03 10 am":"10497858"}

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
        l = driver.find_element_by_xpath(f"//*[@id='Sched.{elements_id[i]}']")
        print(f"Value: {l.text}")

        print(f"Checking {i} if it startswith {i[11]}")
        if l.text.startswith(i[11]):
            params = {"message": f"!!! 我找到 {i} {l.text} 有開放 趕快去訂 !!!"}
            send_line_notification(params)
        else:
            if debug_flag:
                params = {"message": f"*** 自動檢查 台北體育館 {i} 沒有開放. 原因: {l.text}"}
                send_line_notification(params)


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    while True:
        if random.randint(0,20) == 10:
            params = {"message": f"*** 請放心 我還在跑呦"}
            send_line_notification(params)

        check_availability(driver)
        time.sleep(10)

    driver.close()