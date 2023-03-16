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


def getValues(table):
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")    
    
        date = cells[0].text
        value = cells[2].text
        
        if value != "-":
            values_by_date[date] = value

def get3MonthsValues(newDateStart, newDateEnd):
    startDate = driver.find_element(By.NAME, "drought_startdate")
    startDate.clear()
    startDate.send_keys(newDateEnd)

    endDate = driver.find_element(By.NAME, "drought_enddate")
    endDate.clear()
    endDate.send_keys(str(newDateStart))

    dataDensity = Select(driver.find_element(By.ID, "drought_interval"))
    dataDensity.select_by_visible_text("napi")

    dataDensity = Select(driver.find_element(By.ID, "drought_function"))
    dataDensity.select_by_visible_text("minimum - átlag - maximum")

    driver.find_element(By.XPATH, '/html/body/div[1]/form/div[2]/input').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="drought_chart_0_container"]/h1')))

    try: 
        driver.find_element(By.XPATH, '//*[@id="drought_chart_0_container"]/h1/div').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "drought_chart_0_tbl")))

        table = driver.find_element(By.ID, "drought_chart_0_tbl")

        getValues(table)
    except:
        print("No data for this period") 


    

values_by_date = {}

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

for i in range(4):    
    todayDateWithout90days = Without90Days(todayDate)
    print(todayDateWithout90days)
    print(todayDate)
    get3MonthsValues(todayDate, todayDateWithout90days)
    todayDate = todayDateWithout90days
    
#end of the first table
sorted_values_by_date = dict(sorted(values_by_date.items()))
for date, value in sorted_values_by_date.items():
    print(f"{date}: {value}")
print(len(sorted_values_by_date))

driver.quit()
