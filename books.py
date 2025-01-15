# librerias 
import pandas as pd
import sys
import time


import warnings
# Ignorar warnings de pandas sobre cambios futuros
warnings.filterwarnings('ignore', category=FutureWarning)
import logging

# Librerias Selenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # buscar por etiquetas, clases, ids, paths, xpaths
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access variables
email = os.getenv('email')
password = os.getenv('password')



def pagina_principal(url):
    # agregar opciones al driver
    options = Options()

    # Ajustar el custom User-Agent, evitar bloqueos facilmente
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    # Inicializar el webdriver con las opciones personalizadas. 
    driver = webdriver.Chrome(options=options)

    # maximizar pantalla
    driver.maximize_window()

    # Entra a la pagina
    driver.get(url)
    return driver

def sign_in(driver, email, password):


    try:
        # Espera explícita para el enlace de inicio de sesión
        sign_in_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="signIn"]/div/div/a'))
        )
        sign_in_link.click()

        # Espera explícita para el botón de inicio de sesión
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.gr-button.gr-button--dark.gr-button--auth.authPortalConnectButton.authPortalSignInButton'))
        )
        sign_in_button.click()

        # Encuentra el campo de correo electrónico y envía el correo
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(f"{email}")

        # Encuentra el campo de contraseña y envía la contraseña
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(f"{password}")

        # Encuentra y haz clic en el botón de envío
        sign_in_submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signInSubmit"))
        )
        sign_in_submit_button.click()

    except Exception as e:
        print(f"Se produjo un error: {e}")

def go_to_all_genres(driver):
    
    # Espera hasta que el span con el texto "Browse ▾" sea clickeable
    browse_span = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Browse ▾']"))
    )

    # Haz clic en el span
    browse_span.click()

    # Espera hasta que el enlace "All Genres" sea clickeable
    all_genres_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[text()='All Genres']"))
    )

    # Haz clic en el enlace "All Genres"
    all_genres_link.click()

def create_dict():
    books_inf = {
    'books': [],
    'writer': [],
    'rating': [],
    'description': [],
    'statistics': [],
    'details': [],
    'urls': [],
    'gen': [],
    'reading': [],
    'will_read': [],
    'isbn': [],
    'ediciones': [],
    'published': [],
    'format': [],
    'asin': [],
    'language': []
    }
    return books_inf

def get_genres(driver):
    try:
        # Encuentra todos los nombres de géneros
        elements = driver.find_elements(By.CSS_SELECTOR, ".bigBoxContent a.gr-hyperlink")
        names = [element.text for element in elements]
    except TimeoutException:
        logging.error("Error general: No se pudo cargar la lista de géneros (Timeout).")
    except NoSuchElementException:
        logging.error("Error: No se encontraron los géneros en la página.")
    except WebDriverException as e:
        logging.error(f"Error del navegador")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")

    return names[5:6] # solo para el ejemplo

def explore_books(driver, gen): 

    wait = WebDriverWait(driver, 15)

    try:
        # Formatear el XPath con el valor de gen
        xpath = f'//a[@class="actionLink" and contains(text(), "More {gen} books...")]'

        # Espera a que el elemento esté presente en el DOM
        button = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        # Desplázate hasta el elemento para hacerlo visible (si está fuera de la pantalla)
        driver.execute_script("arguments[0].scrollIntoView(true);", button)

        # Verifica si el elemento es clickeable y haz clic
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

        print(f"Botón 'More {gen} books...' clickeado exitosamente.")
    except Exception as e:
        print(f"No se pudo hacer clic en el botón: {e}")

def select_a_genre(driver, genres):

    for gen in genres:
        # Este rango parece estar limitado a 1 género, puedes ajustar el rango según sea necesario
        logging.info(f"Procesando género: {gen}")
        
        try:
            # Esperar que el enlace sea clickeable y hacer clic
            art_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{gen}')]"))
            )
            art_link.click()
            time.sleep(1)  # Pausa para permitir la carga de la página
            
            logging.info(f"Navegando a: {driver.current_url}")
            return gen
        

        except TimeoutException:
            logging.error(f"Error: No se pudo hacer clic en el enlace para '{gen}' (Timeout).")
        except NoSuchElementException:
            logging.error(f"Error: No se encontró el enlace para '{gen}'.")
        except WebDriverException as e:
            logging.error(f"Error del navegador: {e}")

def get_links(driver): 

    URLS = []
    try: 
        logging.info("Proceeding with scraping book URLs...")
        anchor_tag = driver.find_elements(By.XPATH, "//a[starts-with(@href, '/book/show')]")
    
        # Iterate over anchor tags and collect URLs
        for get_href in anchor_tag:
            url = get_href.get_attribute('href')
            URLS.append(url)
            logging.info(f"Found book URL: {url}")
    
    except Exception as e:
        # Log error if no book URLs are found
        logging.error(f"Error occurred while trying to find book URLs")
    
    return URLS

