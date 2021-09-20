from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import time

headers = {
    "Authorization": "Bearer " + "Kr09nUuaYJC05p9kI6UMoxCIbKzyAwZ461ycDzjUWic",
    "Content-Type": "application/x-www-form-urlencoded"
}

url = "https://sports.tms.gov.tw/venues/?K=49#Schedule"
elements_id = {"2021-10-2 10 am":"10497834", "2021-10-3 10 am":"10497858"}

def check_availability():
    driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    #maximize with maximize_window()
    #driver.maximize_window()
    driver.get(url)
    #identify element
    time.sleep(5)
    target = driver.find_element_by_xpath('//*[@id="PickupDateInterFaceBox"]')
    #driver.execute_script('arguments[0].scrollIntoView();', target)
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

        params = {"message": f"{i}: {l.text}"}
        r = requests.post("https://notify-api.line.me/api/notify",
                          headers=headers, params=params)

    driver.close()


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    check_availability()
    