import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient

client = MongoClient('your_connection_string')


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

def send_to_mongodb(values_temp, values_soil10, values_soil20, values_moisture10, values_moisture20):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.weather_data
    temperature = db.temperature
    soil_temperature_10 = db.soil_temperature_10
    soil_temperature_20 = db.soil_temperature_20
    moisture_10 = db.moisture_10
    moisture_20 = db.moisture_20

    for date, value in values_temp.items():
        temperature.insert_one({'date': date, 'value': value})

    for date, value in values_soil10.items():
        soil_temperature_10.insert_one({'date': date, 'value': value})

    for date, value in values_soil20.items():
        soil_temperature_20.insert_one({'date': date, 'value': value})

    for date, value in values_moisture10.items():
        moisture_10.insert_one({'date': date, 'value': value})

    for date, value in values_moisture20.items():
        moisture_20.insert_one({'date': date, 'value': value})

    client.close()

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
    

#mongodb send values
send_to_mongodb(values_temp, values_soil10, values_soil20, values_moisture10, values_moisture20)

driver.quit()
