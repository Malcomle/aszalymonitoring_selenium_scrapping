from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import time
import os

import csv

url = 'https://aszalymonitoring.vizugy.hu/index.php?view=customgraph'

chrome_options = webdriver.ChromeOptions()
# Uncomment the following line if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")

chromedriver_path = "./chromedriver"
s = Service(executable_path=chromedriver_path)

driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get(url)


elem = driver.find_element(By.CLASS_NAME, "infodiv")
print(elem.get_attribute("innerHTML"))

select = Select(driver.find_element(By.XPATH, "//*[@id='drought_station']"))
select.select_by_visible_text("Csolnok")

startDate = driver.find_element(By.NAME, "drought_startdate")
startDate.clear()
startDate.send_keys("2023-03-01")

endDate = driver.find_element(By.NAME, "drought_enddate")
endDate.clear()
endDate.send_keys("2023-03-16")

dataDensity = Select(driver.find_element(By.ID, "drought_interval"))
dataDensity.select_by_visible_text("napi")

driver.find_element(By.XPATH, '/html/body/div[1]/form/div[2]/input').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "drought_chart_0_container")))

elem = driver.find_element(By.CLASS_NAME, "drought_memo")
print(elem.get_attribute("innerHTML"))


driver.quit()
