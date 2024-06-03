import re
import json
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Configurar ruta al archivo CSV
ruta_csv = r'C:\Users\MALVARE5\OneDrive - Capgemini\Desktop\Facturas\Invoices ELM.csv'
# Leer el archivo CSV
df = pd.read_csv(ruta_csv)
# Asegúrate de que las columnas del CSV se llamen 'NumeroFactura' y 'NombreCuenta'
facturas = df[['NumeroFactura', 'NombreCuenta']]

# Configurar el WebDriver (suponiendo que usas Chrome)
download_path = r'C:\Users\MALVARE5\OneDrive - Capgemini\Desktop\Facturas'
credentials_file = 'credentials.json'

def load_credentials(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def configure_driver(download_path):
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_path,
        "savefile.default_directory": download_path,
        "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}',
        "printing.default_destination_selection_rules": '{"kind":"local","id":"Save as PDF"}'
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--kiosk-printing")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def esperar_elemento(driver, by, value, tiempo=15):
    return WebDriverWait(driver, tiempo).until(EC.presence_of_element_located((by, value)))

def limpiar_nombre(nombre):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', nombre)

def iniciar_sesion(driver, credenciales):
    driver.get(credenciales['login_url'])
    time.sleep(3)
    try:
        user_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        user_field.send_keys(credenciales['username'])
        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(credenciales['password'])
        password_field.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        driver.quit()
        exit()
    time.sleep(5)

def buscar_factura(driver, numero_factura):
    try:
        search_bar = esperar_elemento(driver, By.ID, 'uif38 input')
    except:
        print("No se pudo encontrar la barra de búsqueda con ID 'uif38 input'. Intentando con CLASS.")
        try:
            search_bar = esperar_elemento(driver, By.CLASS_NAME, 'uif750')
        except:
            print("No se pudo encontrar la barra de búsqueda con CLASS 'uif750'. Intentando con XPATH.")
            search_bar = esperar_elemento(driver, By.XPATH, '//input[@placeholder="Search"]')
    search_bar.clear()
    search_bar.send_keys(numero_factura)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(3)

def imprimir_factura(driver, numero_factura, nombre_cuenta):
    try:
        PDFboton_imprimir = esperar_elemento(driver, By.XPATH, '//span[@id="spn_PRINT_d1"]//a[contains(@class, "pgm_menu_print")]')
    except:
        print("No se pudo encontrar el botón de impresión.")
        return False
    time.sleep(3)
    actions = ActionChains(driver)
    actions.move_to_element(PDFboton_imprimir).perform()
    try:
        primer_resultado = esperar_elemento(driver, By.XPATH, '//*[@id="nl1"]/a')
        primer_resultado.click()
    except:
        print("No se pudo encontrar el primer resultado de impresión.")
        return False
    time.sleep(3)
    try:
        opcion_print = esperar_elemento(driver, By.XPATH, '//span[@id="spn_PRINT_d1"]//a[contains(@class, "pgm_menu_print")]//div[contains(@class, "button-print")]')
        opcion_print.click()
    except:
        print("No se pudo encontrar la opción de impresión.")
        return False
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    driver.execute_script('window.print();')
    time.sleep(5)
    files = [f for f in os.listdir(download_path) if f.endswith('.pdf')]
    if files:
        downloaded_file = max([os.path.join(download_path, f) for f in files], key=os.path.getctime)
        nuevo_nombre_archivo = f'{numero_factura}_{nombre_cuenta}.pdf'
        ruta_archivo = os.path.join(download_path, nuevo_nombre_archivo)
        os.rename(downloaded_file, ruta_archivo)
        print(f"Factura {numero_factura} de {nombre_cuenta} descargada correctamente como {nuevo_nombre_archivo}.")
        return True
    else:
        print(f"Error al descargar la factura {numero_factura} de {nombre_cuenta}.")
        return False
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def main():
    credenciales = load_credentials(credentials_file)
    driver = configure_driver(download_path)
    iniciar_sesion(driver, credenciales)
    os.makedirs(download_path, exist_ok=True)
    for index, row in facturas.iterrows():
        numero_factura = limpiar_nombre(str(row['NumeroFactura']))
        nombre_cuenta = limpiar_nombre(str(row['NombreCuenta']))
        buscar_factura(driver, numero_factura)
        if not imprimir_factura(driver, numero_factura, nombre_cuenta):
            continue
    driver.quit()
    os.remove(credentials_file)
    print("Archivo credentials.json eliminado.")

if __name__ == "__main__":
    main()
