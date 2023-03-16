import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient

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

            date = cells[0].text
            if date not in weather_data:
                weather_data[date] = {}

            if cells[2].text != "-" or cells[1].text != "-":
                if type == "temp":
                    weather_data[date]['temp'] = cells[2].text
                if type == "soil":
                    weather_data[date]['soil10'] = cells[1].text
                    weather_data[date]['soil20'] = cells[2].text
                if type == "moisture":
                    weather_data[date]['moisture10'] = cells[1].text
                    weather_data[date]['moisture20'] = cells[2].text
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

def send_to_mongodb(station, weather_data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.weather_data

    # Créez une collection avec le nom de la station
    weather_collection = db[station]

    for date, data in weather_data.items():
        document = {
            "date": date,
            "data": data
        }
        weather_collection.insert_one(document)

    client.close()


weather_data = {}

url = 'https://aszalymonitoring.vizugy.hu/index.php?view=customgraph'

chrome_options = webdriver.ChromeOptions()
chromedriver_path = "./chromedriver"
s = Service(executable_path=chromedriver_path)

driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get(url)

select = Select(driver.find_element(By.XPATH, "//*[@id='drought_station']"))
select.select_by_visible_text("Csolnok")

todayDate = datetime.date.today().strftime('%Y-%m-%d')

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
    
send_to_mongodb("Csolnok", weather_data)

driver.quit()