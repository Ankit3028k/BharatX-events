import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, InvalidSessionIdException, WebDriverException

def initialize_driver(base_download_path, state, district, ac_name):
    """Initialize Chrome WebDriver with specified download path for state, district, and assembly."""
    print("Setting up Chrome WebDriver...")
    # Create directory structure: Bihar/District/Assembly
    download_path = os.path.join(base_download_path, state, district, ac_name)
    os.makedirs(download_path, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        return driver, download_path
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        raise

def wait_for_spinner_to_disappear(driver, timeout=60):
    """Wait for the globalSpinnerDiv to disappear."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.globalSpinnerDiv"))
        )
        print("      Spinner disappeared")
        return True
    except TimeoutException:
        print("      Timeout waiting for spinner to disappear")
        return False
    except InvalidSessionIdException:
        print("      Session invalid during spinner check")
        return False

def reset_page_state(driver, state="Bihar", district=None, ac_name=None, roll_type="f", lang=None, retries=3):
    """Reset page to select state, district, assembly constituency, roll type, and language."""
    for attempt in range(1, retries + 1):
        try:
            print(f"      Resetting page state (Attempt {attempt})...")
            driver.get("https://voters.eci.gov.in/download-eroll")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("      Page loaded successfully")

            # Check session validity
            driver.execute_script("return document.title;")
            print("      Session valid before selections")

            # Select State
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, "stateCode"))
            ).click()
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"//select[@name='stateCode']/option[text()='{state}']"))
            ).click()
            print(f"      Selected state: {state}")
            time.sleep(3)

            # Select District
            if district:
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//select[@name='district']/option[text()='{district}']"))
                ).click()
                print(f"      Selected district: {district}")
                time.sleep(4)

            # Select Assembly Constituency
            if ac_name:
                try:
                    ac_dropdown = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "div.css-b62m3t-container div[class*='control']")
                        )
                    )
                    ac_dropdown.click()
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[text()='{ac_name}']"))
                    ).click()
                    print(f"      Selected assembly constituency: {ac_name}")
                    time.sleep(2)
                except TimeoutException:
                    print("      Timeout waiting for AC dropdown. Trying alternative selector.")
                    ac_dropdown = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//label[contains(text(), 'Assembly Constituency')]/ancestor::div[@class='row']//div[contains(@class, 'control')]")
                        )
                    )
                    ac_dropdown.click()
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[text()='{ac_name}']"))
                    ).click()
                    print(f"      Selected assembly constituency via alternative selector: {ac_name}")
                    time.sleep(2)

            # Select Roll Type
            if roll_type:
                wait_for_spinner_to_disappear(driver)
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.NAME, "roleType"))
                ).click()
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//select[@name='roleType']/option[@value='{roll_type}']"))
                ).click()
                print(f"      Selected roll type: Final Roll - 2025")
                time.sleep(2)

            # Select Language if provided
            if lang:
                wait_for_spinner_to_disappear(driver)
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.NAME, "langCd"))
                ).click()
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//select[@name='langCd']/option[@value='{lang}']"))
                ).click()
                print(f"      Selected language: {lang}")
                time.sleep(2)

            return True

        except Exception as e:
            print(f"      Failed to reset page state (Attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(5)
                continue
            return False
    return False

def solve_captcha(driver, max_attempts=5):
    """Wait for user to input 6-character CAPTCHA and click download."""
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            # Check session validity
            driver.execute_script("return document.title;")
            print("      Session valid before CAPTCHA input")

            # Wait for CAPTCHA input
            captcha_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "captcha"))
            )
            captcha_input.clear()
            print("      Waiting for user to input 6-character CAPTCHA (120 seconds)...")

            # Wait until 6 chars are entered
            WebDriverWait(driver, 120).until(
                lambda d: len(captcha_input.get_attribute("value")) == 6
            )
            captcha_text = captcha_input.get_attribute("value")
            print(f"      User entered CAPTCHA: {captcha_text}")

            # Click Download button
            download_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-block.submit"))
            )
            driver.execute_script("arguments[0].click();", download_btn)
            print("      Download button clicked.")

            # Check for error
            try:
                error_msg = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".error, .alert, [role='alert']"))
                ).text
                print(f"      CAPTCHA error: {error_msg} → Retrying...")
                driver.find_element(By.CSS_SELECTOR, "img[alt='refresh']").click()
                time.sleep(3)
                continue
            except TimeoutException:
                print("      CAPTCHA accepted.")
                return True

        except Exception as e:
            print(f"      Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                try:
                    driver.find_element(By.CSS_SELECTOR, "img[alt='refresh']").click()
                    time.sleep(3)
                except:
                    pass
            else:
                print("      Max CAPTCHA attempts reached.")
                return False
    return False

def wait_for_downloads_complete(download_path, expected_pdfs, timeout=600):
    """Wait until expected number of PDFs are downloaded."""
    print(f"      Waiting for {expected_pdfs} PDFs in {download_path}...")
    start_time = time.time()
    downloaded_files = set()
    while time.time() - start_time < timeout:
        if not any(fname.endswith('.crdownload') for fname in os.listdir(download_path)):
            pdf_files = set(glob.glob(os.path.join(download_path, "*.pdf")))
            new_files = pdf_files - downloaded_files
            if new_files:
                print(f"      Found new PDF(s): {list(new_files)}")
                downloaded_files.update(new_files)
            if len(downloaded_files) >= expected_pdfs:
                print(f"      All {len(downloaded_files)} expected PDFs downloaded.")
                return downloaded_files
        time.sleep(2)
    print(f"      Timeout. Only {len(downloaded_files)} PDFs downloaded.")
    return downloaded_files

def count_table_parts(driver):
    """Count number of rows and selected checkboxes."""
    try:
        parts_table_body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".datatable-box tbody"))
        )
        rows = parts_table_body.find_elements(By.TAG_NAME, "tr")
        print(f"      Found {len(rows)} part(s).")

        selected_count = sum(
            1 for row in rows if row.find_element(By.CSS_SELECTOR, "input[type='checkbox']").is_selected()
        )
        print(f"      {selected_count} part(s) already selected.")
        return len(rows), selected_count, rows
    except Exception as e:
        print(f"      Error counting table parts: {e}")
        return 0, 0, []

def get_table_identifier(rows):
    """Get a unique identifier for the current table content."""
    return ''.join([row.text for row in rows])

def navigate_to_next_page(driver, retries=3):
    """Click the pagination '>' button with robust selectors and content check."""
    for attempt in range(1, retries + 1):
        try:
            print(f"      Attempt {attempt}: Navigating to next page...")

            # Wait for table to be stable and get current identifier
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".datatable-box tbody"))
            )
            _, _, rows = count_table_parts(driver)
            before_id = get_table_identifier(rows)
            print(f"      Before navigation table ID: {before_id[:50]}...")  # Truncated for log

            # Find all control buttons
            control_buttons = driver.find_elements(By.CSS_SELECTOR, "button.control-btn")
            next_button = None
            for btn in control_buttons:
                btn_text = btn.text.strip()
                if btn_text == '>' or btn_text == '&gt;':
                    next_button = btn
                    print("      Found next button with text: " + btn_text)
                    break

            if not next_button:
                print("      No next button found. Dumping button texts for debugging...")
                for btn in control_buttons:
                    print(f"      Button text: {btn.text.strip()}")
                return False

            # Check disabled state
            if "disabled" in next_button.get_attribute("outerHTML"):
                print("      Next page button is disabled → No more pages.")
                return False

            # Click safely
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_button)
            print("      Clicked next page button.")

            # Wait for update
            time.sleep(1)
            wait_for_spinner_to_disappear(driver, 30)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".datatable-box tbody"))
            )

            # Check if content changed
            _, _, new_rows = count_table_parts(driver)
            after_id = get_table_identifier(new_rows)
            print(f"      After navigation table ID: {after_id[:50]}...")
            if after_id == before_id:
                print("      Table content did not change → No more pages.")
                return False

            print("      New page loaded successfully.")
            return True

        except Exception as e:
            print(f"      Attempt {attempt}: Failed to navigate → {e}")
            time.sleep(2)

    print("      Max navigation attempts reached.")
    return False

def test_captcha():
    base_download_path = os.path.abspath("PDFs")
    state = "Bihar"
    district = "ARARIA"
    assemblies = ["46 - Narpatganj", "47 - Raniganj"]  # Example: Add more assemblies as needed

    for ac_name in assemblies:
        driver = None
        try:
            # Initialize driver with specific download path for this assembly
            driver, download_path = initialize_driver(base_download_path, state, district, ac_name)
            print(f"Downloading PDFs for {state}/{district}/{ac_name} into {download_path}")

            if not reset_page_state(driver, state=state, district=district, ac_name=ac_name, roll_type="f", lang="HIN"):
                print(f"Critical error: Failed to reset page state for {ac_name} after retries.")
                continue

            page = 1
            total_downloaded = 0

            while True:
                print(f"\nProcessing page {page} for {ac_name}...")

                # Count parts
                total_parts, selected_parts, _ = count_table_parts(driver)
                if total_parts == 0:
                    print("      No parts found, moving to next assembly.")
                    break

                # Select All
                try:
                    select_all_checkbox = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, "selectAll"))
                    )
                    driver.execute_script("arguments[0].click();", select_all_checkbox)
                    time.sleep(2)
                except Exception as e:
                    print(f"      Error selecting all checkboxes: {e}")
                    break

                total_parts, selected_parts, _ = count_table_parts(driver)
                if selected_parts == 0:
                    print("      No parts selected, moving to next assembly.")
                    break

                # Wait 10 seconds before CAPTCHA
                print("      Waiting 10 seconds for CAPTCHA to load...")
                time.sleep(10)

                # Verify session before CAPTCHA
                try:
                    driver.execute_script("return document.title;")
                    print("      Session valid before CAPTCHA")
                except InvalidSessionIdException:
                    print("      Session invalid before CAPTCHA, exiting")
                    break

                # Solve CAPTCHA & Download
                if not solve_captcha(driver):
                    print("      CAPTCHA failed.")
                    break

                # Wait for downloads
                downloaded_files = wait_for_downloads_complete(download_path, selected_parts + total_downloaded, timeout=600)
                new_downloaded = len(downloaded_files) - total_downloaded
                total_downloaded = len(downloaded_files)
                print(f"      Page {page} → {new_downloaded} new PDFs, total so far: {total_downloaded}")

                # Next page
                if not navigate_to_next_page(driver):
                    print(f"      Finished all pages for {ac_name}.")
                    break
                page += 1

        except Exception as e:
            print(f"Critical error for {ac_name}: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                    print(f"Browser closed for {ac_name}.")
                except Exception as e:
                    print(f"Error closing browser for {ac_name}: {e}")

if __name__ == "__main__":
    test_captcha()