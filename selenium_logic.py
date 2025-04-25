from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Inicjalizacja przeglądarki (ukryta)
options = Options()
options.add_argument("--headless=new")  # Ukryj przeglądarkę
options.add_argument("--window-size=1920,1080")  # Udawaj pełne okno
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# 🔐 Funkcja logowania
def login_to_mycloud(email, password):
    driver.get("https://home.mycloud.com")

    # Akceptacja cookies
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "truste-consent-button")))
        cookie_button.click()
        print("🍪 Kliknięto Accept cookies.")
    except:
        print("🍪 Cookies nie wymagały akceptacji.")

    time.sleep(2)  # Daj chwilę stronie się załadować

    # Kliknięcie Zaloguj się
    if not click_login_link():
        print("❌ Nie udało się znaleźć przycisku Zaloguj się.")
        return

    # Wpisanie emaila
    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    email_input.send_keys(email)
    print("📧 Email wpisany.")

    # Wpisanie hasła
    password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    password_input.send_keys(password)
    print("🔐 Hasło wpisane.")

    # Kliknięcie Kontynuuj
    continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontynuuj')]")))
    continue_button.click()
    print("➡️ Kliknięto Kontynuuj.")

    time.sleep(8)
    print("✅ Zalogowano!")

# 🔎 Funkcja klikająca prawidłowy przycisk Zaloguj się
def click_login_link():
    print("🔍 Szukam przycisku 'Zaloguj się'...")
    try:
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'Button--secondary') and contains(text(), 'Zaloguj się')]")
            )
        )
        login_button.click()
        print("➡️ Kliknięto przycisk 'Zaloguj się'")
        return True

    except Exception as e:
        print(f"❌ Nie znaleziono przycisku 'Zaloguj się': {e}")
        return False

# 📂 Funkcja listowania plików i folderów
def list_files_selenium(driver, path=""):
    files = []
    seen = set()

    if path:
        print(f"➡️ Przechodzę do folderu: {path}")
        try:
            folder = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{path}')]"))
            )
            folder.click()
            time.sleep(2)
        except:
            print(f"⚠️ Nie udało się kliknąć folderu: {path}")
    else:
        driver.get("https://home.mycloud.com/cloud/file")
        time.sleep(3)

        print("➡️ Próbuję kliknąć 'Pliki i foldery'...")
        try:
            link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Pliki i foldery')]"))
            )
            link.click()
            time.sleep(3)
            print("✅ Kliknięto 'Pliki i foldery'")
        except:
            print("⚠️ Nie udało się kliknąć 'Pliki i foldery'")

    print("🔍 Szukam faktycznych plików/folderów...")

    items = driver.find_elements(By.CSS_SELECTOR, "div")

    forbidden = [
        "dodaj pliki", "więcej możliwości", "kopiuj usb",
        "ustawienia", "wyślij opinię", "pomoc",
        "pliki i foldery", "zdjęcia", "albumy", "współdzielony",
        "nazwa", "foldery", "piotr kawa", "kawjorek321",
        "funkcja importu", "funkcja google", "opinia", "pomoc"
    ]

    for elem in items:
        try:
            text = elem.text.strip()
            lines = text.split("\n")

            if len(lines) >= 1:
                name = lines[0].strip()

                is_email = "@" in name and "." in name
                is_date_or_separator = any(day in name.lower() for day in ["pon", "wt", "śr", "czw", "pt", "sob", "niedz"]) or "-" in name
                is_forbidden = any(bad in name.lower() for bad in forbidden)

                if (
                    name
                    and len(name) > 2
                    and not is_email
                    and not is_date_or_separator
                    and not is_forbidden
                    and name not in seen
                ):
                    if any(ext in name.lower() for ext in [".jpg", ".png", ".mp4", ".pdf", ".docx", ".txt", ".zip"]):
                        type_ = "file"
                    else:
                        type_ = "folder"

                    print(f"🧩 Dodaję do GUI: {name} (type={type_})")
                    files.append({"name": name, "type": type_, "path": name})
                    seen.add(name)

        except Exception as e:
            continue

    print(f"🔁 Zwracam {len(files)} plików/folderów do GUI")
    return files
