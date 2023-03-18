import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient

def without_90_days(actual_date):
    actual_date = datetime.datetime.strptime(actual_date, '%Y-%m-%d').date()
    delta = datetime.timedelta(days=90)
    today_date_without_90_days = actual_date - delta
    start_date_string = today_date_without_90_days.strftime('%Y-%m-%d')
    return start_date_string

def select_option_by_text(element_id, text):
    select = Select(driver.find_element(By.ID, element_id))
    select.select_by_visible_text(text)

def get_values(type):
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
 
def get_temperature_values():   
    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text("Levegőhőmérséklet (°C)")

    operation = Select(driver.find_element(By.ID, "drought_function"))
    operation.select_by_visible_text("minimum - átlag - maximum")   

    get_values("temp")

def get_soil_temperature_values():
    operation = Select(driver.find_element(By.ID, "drought_function"))
    operation.select_by_visible_text("átlag")

    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text("Talajhőmérséklet(10 cm) (°C)")

    driver.find_element(By.ID, 'drought_add_parameter_btn').click()

    parameters = Select(driver.find_element(By.ID, "drought_parameter_1"))
    parameters.select_by_visible_text("Talajhőmérséklet(20 cm) (°C)")

    get_values("soil")

    driver.find_element(By.ID, 'drought_parameter_1_btn').click()

def get_moisture_temperature_values(value):
    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text(value)

    get_values("moisture")   

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

def get_station_data(station):
    select_option_by_text("drought_station", station)

    today_date = datetime.date.today().strftime('%Y-%m-%d')

    for i in range(4):    
        today_date_without_90_days = without_90_days(today_date)

        start_date = driver.find_element(By.NAME, "drought_startdate")
        start_date.clear()
        start_date.send_keys(today_date_without_90_days)

        end_date = driver.find_element(By.NAME, "drought_enddate")
        end_date.clear()
        end_date.send_keys(str(today_date))

        select_option_by_text("drought_interval", "napi")

        get_temperature_values()
        get_soil_temperature_values()
        get_moisture_temperature_values("Talajnedvesség(10 cm) (V/V %)")
        get_moisture_temperature_values("Talajnedvesség(20 cm) (V/V %)")
        today_date = today_date_without_90_days
        
        send_to_mongodb(station, weather_data)

weather_data = {}

url = 'https://aszalymonitoring.vizugy.hu/index.php?view=customgraph'

chrome_options = webdriver.ChromeOptions()
chromedriver_path = "./chromedriver"
s = Service(executable_path=chromedriver_path)

driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get(url)

stations = ["Csolnok", "Tata"]
for station in stations:
    print(station)
    get_station_data(station)

driver.quit()