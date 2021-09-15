from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
# maximize with maximize_window()
driver.maximize_window()
driver.get("https://www.tutorialspoint.com/index.htm")
# identify element
l=driver.find_element_by_css_selector("h4")
# get text and print
print("Text is: " + l.text)
driver.close()