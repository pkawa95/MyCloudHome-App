from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login_and_get_token(email, password):
    options = Options()
    options.add_argument("--start-maximized")  # widoczne okno dla debugowania
    # options.add_argument("--headless=new")   # odkomentuj później na produkcję

    driver = webdriver.Chrome(options=options)

    try:
        wait = WebDriverWait(driver, 20)

        print("🌐 Otwieram MyCloud...")
        driver.get("https://home.mycloud.com")

        # 🔹 Akceptuj cookies
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "truste-consent-button")))
            cookie_button.click()
            print("🍪 Kliknięto Accept cookies.")
        except:
            print("⚠️ Nie trzeba klikać cookies.")

        # Teraz kliknij dokładnie 'Zaloguj się'
        try:
            login_links = driver.find_elements(By.TAG_NAME, "a")
            for link in login_links:
                href = link.get_attribute("href") or ""
                text = link.text.strip()

                if "Zaloguj się" in text and "authorize" in href and "westerndigital.com/wd/" not in href:
                    link.click()
                    print(f"➡️ Kliknięto prawidłowy link 'Zaloguj się' ({href})")
                    break
            else:
                print("⚠️ Nie znaleziono poprawnego linku 'Zaloguj się'")
        except Exception as e:
            print(f"❌ Błąd przy klikaniu 'Zaloguj się': {e}")

        # 🔹 Wpisz email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_input.send_keys(email)
        print("📧 Email wpisany.")

        # 🔹 Wpisz hasło
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(password)
        print("🔐 Hasło wpisane.")

        # 🔹 Kliknij "Kontynuuj"
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontynuuj')]")))
        continue_button.click()
        print("➡️ Kliknięto Kontynuuj.")

        # 🔹 Poczekaj chwilę na redirect
        time.sleep(10)

        # 🔹 Spróbuj pobrać token z localStorage
        token = driver.execute_script("return window.localStorage.getItem('accessToken');")

        if not token:
            print("⚠️ Token nie znaleziony w localStorage. Sprawdzam sessionStorage...")
            token = driver.execute_script("return window.sessionStorage.getItem('accessToken');")

        if token:
            print("✅ Access token zdobyty!")
            return token

        # 🔍 Jeśli nadal brak – sprawdź URL i ciasteczka
        print("🔍 Token nie znaleziony w storage. Sprawdzam current_url i ciasteczka...")

        current_url = driver.current_url
        print(f"🌐 Finalny URL: {current_url}")

        for cookie in driver.get_cookies():
            print(f"🍪 {cookie['name']} = {cookie['value']}")

        return None

    finally:
        driver.quit()
