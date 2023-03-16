import datetime
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

def Without90Days(actualDate):
    actualDate = datetime.datetime.strptime(actualDate, '%Y-%m-%d').date()
    delta = datetime.timedelta(days=90)
    todayDateWithout90days = actualDate - delta
    startDateString = todayDateWithout90days.strftime('%Y-%m-%d')
    return startDateString


def getValues(type):
    driver.find_element(By.XPATH, '/html/body/div[1]/form/div[2]/input').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="drought_chart_0_container"]/h1')))

    try: 
        driver.find_element(By.XPATH, '//*[@id="drought_chart_0_container"]/h1/div').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "drought_chart_0_tbl")))

        table = driver.find_element(By.ID, "drought_chart_0_tbl")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")    

            if cells[2].text != "-" or cells[1].text != "-":
                if type == "temp":
                    values_temp[cells[0].text] = cells[2].text
                if type == "soil":
                    values_soil10[cells[0].text] = cells[1].text
                    values_soil20[cells[0].text] = cells[2].text
                if type == "moisture":
                    values_moisture10[cells[0].text] = cells[1].text
                    values_moisture20[cells[0].text] = cells[2].text
    except:
        print("No data for this period")    

def getTemparturesValues():   
    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text("Levegőhőmérséklet (°C)")

    operation = Select(driver.find_element(By.ID, "drought_function"))
    operation.select_by_visible_text("minimum - átlag - maximum")   

    getValues("temp")

def getSoilTemparturesValues():
    operation = Select(driver.find_element(By.ID, "drought_function"))
    operation.select_by_visible_text("átlag")

    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text("Talajhőmérséklet(10 cm) (°C)")

    driver.find_element(By.ID, 'drought_add_parameter_btn').click()

    parameters = Select(driver.find_element(By.ID, "drought_parameter_1"))
    parameters.select_by_visible_text("Talajhőmérséklet(20 cm) (°C)")

    getValues("soil")

    driver.find_element(By.ID, 'drought_parameter_1_btn').click()

def getMoistureTemparturesValues(value):
    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text(value)

    getValues("moisture")   

values_temp = {}
values_soil10 = {}
values_soil20 = {}
values_moisture10 = {}
values_moisture20 = {}

url = 'https://aszalymonitoring.vizugy.hu/index.php?view=customgraph'

chrome_options = webdriver.ChromeOptions()
# Uncomment the following line if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")

chromedriver_path = "./chromedriver"
s = Service(executable_path=chromedriver_path)

driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get(url)

select = Select(driver.find_element(By.XPATH, "//*[@id='drought_station']"))
select.select_by_visible_text("Csolnok")

# boucle 3 times
todayDate = datetime.date.today().strftime('%Y-%m-%d')

#get temperatures
for i in range(4):    
    todayDateWithout90days = Without90Days(todayDate)

    startDate = driver.find_element(By.NAME, "drought_startdate")
    startDate.clear()
    startDate.send_keys(todayDateWithout90days)

    endDate = driver.find_element(By.NAME, "drought_enddate")
    endDate.clear()
    endDate.send_keys(str(todayDate))

    dataDensity = Select(driver.find_element(By.ID, "drought_interval"))
    dataDensity.select_by_visible_text("napi")

    getTemparturesValues()
    getSoilTemparturesValues()
    getMoistureTemparturesValues("Talajnedvesség(10 cm) (V/V %)")
    getMoistureTemparturesValues("Talajnedvesség(20 cm) (V/V %)")
    todayDate = todayDateWithout90days
    

#end of the first table
sorted_values_by_date = dict(sorted(values_temp.items()))
for date, value in sorted_values_by_date.items():
    print(f"{date}: {value}")
print(len(sorted_values_by_date))
print(len(values_soil10))
print(len(values_soil20))

driver.quit()
