# Documentation technique pour un scrapper Selenium

Cette documentation technique couvre la création d'un scrapper en Python à l'aide de Selenium pour extraire les données météorologiques du site **[https://aszalymonitoring.vizugy.hu/index.php?view=customgraph](https://aszalymonitoring.vizugy.hu/index.php?view=customgraph)** et les stocker dans une base de données MongoDB.

---

## **Prérequis**

Pour exécuter ce script, vous aurez besoin de :

- Python 3.x
- Les bibliothèques suivantes :
    - **`selenium`**
    - **`pymongo`**
- Le fichier **`constant.py`** contenant les constantes nécessaires.
- Le fichier **`chromedriver`** correspondant à votre navigateur internet.

---

## **Installation**

Installez les bibliothèques requises en utilisant pip :

```jsx
pip install selenium pymongo
```

---

## **Structure du projet**

Le projet se compose de deux fichiers principaux :

- **`aszalymonitoring_selenium.py`**: le script principal pour récupérer les données météorologiques.
- **`constant.py`**: un fichier contenant les constantes utilisées dans le script principal.

---

## **Utilisation**

1. Modifiez le fichier **`constant.py`** pour inclure le bon chemin vers le fichier **`chromedriver`** (ajoutez **`.exe`** si vous êtes sous Windows) et la liste des stations pour lesquelles vous souhaitez récupérer les données.

```python
CHROME_DRIVER_PATH = "./chromedriver"  # ajoutez .exe si vous êtes sous Windows
WEBSITE_URL = "[https://aszalymonitoring.vizugy.hu/index.php?view=customgraph](https://aszalymonitoring.vizugy.hu/index.php?view=customgraph)"
STATIONS = ["Csolnok", "Tata"]
```

2. Exécutez le script **`aszalymonitoring_selenium.py`** à l'aide de la commande suivante :

```python
python aszalymonitoring_selenium.py
```

3. Le script récupérera les données météorologiques des stations spécifiées dans le fichier **`constant.py`** et les stockera dans une base de données MongoDB locale. Chaque station aura sa propre collection nommée d'après le nom de la station.

---

## **Fonctionnement du script**

Le script utilise la bibliothèque Selenium pour naviguer sur le site web et interagir avec les éléments de la page. Il récupère les données de température, de température du sol et d'humidité du sol pour chaque station et les stocke dans un dictionnaire **`weather_data`**. Les données sont ensuite envoyées à une base de données MongoDB locale.

Les fonctions principales du script sont :

- **`without_90_days(actual_date)`**: calcule la date 90 jours avant la date donnée.
- **`select_option_by_text(element_id, text)`**: sélectionne une option d'un élément de type **`select`** en fonction du texte visible.
- **`get_values(type)`**: récupère les valeurs météorologiques du tableau sur la page et les stocke dans le dictionnaire **`weather_data`**.
- **`get_temperature_values()`**, **`get_soil_temperature_values()`**, **`get_moisture_temperature_values(value)`**: des fonctions pour sélectionner les paramètres appropriés pour chaque type de données et appeler la fonction **`get_values()`**.
- **`send_to_mongodb(station, weather_data)`**: envoie les données météorologiques à la base de données MongoDB locale.
- **`get_station_data(station)`**: récupère les données météorologiques pour une station donnée et les stocke dans le dictionnaire **`weather_data`**.
- La boucle principale du script parcourt la liste des stations spécifiées dans le fichier **`constant.py`** et appelle la fonction **`get_station_data()`** pour chaque station.

---

## **Structure des données**

Les données météorologiques sont stockées dans une base de données MongoDB locale. Chaque station a sa propre collection, nommée d'après le nom de la station.

Les documents dans les collections ont la structure suivante :

```python
{
    "date": "2023-03-26",
    "data": {
        "temp": "12.5",
        "soil10": "10.2",
        "soil20": "9.8",
        "moisture10": "22.3",
        "moisture20": "21.8"
    }
}
```

- **`date`**: la date des données météorologiques.
- **`data`**: un dictionnaire contenant les données météorologiques.
    - **`temp`**: la température de l'air (°C).
    - **`soil10`**: la température du sol à 10 cm de profondeur (°C).
    - **`soil20`**: la température du sol à 20 cm de profondeur (°C).
    - **`moisture10`**: l'humidité du sol à 10 cm de profondeur (V/V %).
    - **`moisture20`**: l'humidité du sol à 20 cm de profondeur (V/V %).