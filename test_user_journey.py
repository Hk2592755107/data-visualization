from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()  # Make sure chromedriver is in PATH

# --- Start Test ---
def wait_for(selector, by=By.CSS_SELECTOR, timeout=10):
    """Wait for an element to appear (up to timeout seconds)."""
    for _ in range(timeout * 2):
        try:
            elem = driver.find_element(by, selector)
            if elem.is_displayed():
                return elem
        except:
            pass
        time.sleep(0.5)
    raise Exception(f"Timeout waiting for {selector}")

try:
    driver.get("http://localhost:5000/medicines")
    print("Opened /medicines page.")

    # --- Add Medicine ---
    wait_for("#openAddModal").click()
    print("Opened Add Medicine Modal.")
    time.sleep(0.5)
    driver.find_element(By.NAME, "name").send_keys("TestMed123")
    driver.find_element(By.NAME, "brand").send_keys("TestBrand")
    driver.find_element(By.NAME, "quantity").send_keys("15")
    driver.find_element(By.NAME, "price").send_keys("99.95")
    driver.find_element(By.NAME, "expiry_date").send_keys("2030-12-31")
    # Pick category (1st one)
    cat_select = driver.find_element(By.NAME, "category")
    cat_select.click()
    cat_select.send_keys(Keys.DOWN, Keys.ENTER)
    # Pick supplier (1st one)
    supp_select = driver.find_element(By.NAME, "supplier_id")
    supp_select.click()
    supp_select.send_keys(Keys.DOWN, Keys.ENTER)
    # Submit
    driver.find_element(By.CSS_SELECTOR, "#addForm button[type='submit']").click()
    print("Submitted Add Medicine.")
    time.sleep(2)

    # --- Add Customer ---
    driver.get("http://localhost:5000/customers")
    print("Opened /customers page.")
    wait_for("button.btn-primary").click()
    print("Opened Add Customer Modal.")
    time.sleep(0.5)
    driver.find_element(By.NAME, "name").send_keys("Test Customer")
    driver.find_element(By.NAME, "contact_number").send_keys("1234567890")
    driver.find_element(By.NAME, "email").send_keys("test@mailinator.com")
    driver.find_element(By.CSS_SELECTOR, "#customerForm button[type='submit']").click()
    print("Submitted Add Customer.")
    time.sleep(2)

    # --- Sell Medicine ---
    driver.get("http://localhost:5000/medicines")
    wait_for("#openSellModal").click()
    print("Opened Sell Medicine Modal.")
    time.sleep(1)
    # Select customer (first one)
    cust_select = wait_for("#customer_id")
    cust_select.click()
    cust_select.send_keys(Keys.DOWN, Keys.ENTER)
    # Select medicine (first row)
    med_select = driver.find_element(By.NAME, "medicine_id")
    med_select.click()
    med_select.send_keys(Keys.DOWN, Keys.ENTER)
    driver.find_element(By.NAME, "quantity").send_keys("2")
    driver.find_element(By.NAME, "discount").clear()
    driver.find_element(By.NAME, "discount").send_keys("0")
    driver.find_element(By.CSS_SELECTOR, "#saleForm button[type='submit']").click()
    print("Submitted Sell Medicine.")
    time.sleep(2)

    # --- Check Toast Message (success) ---
    try:
        toast = wait_for("#toastBody")
        print("TOAST:", toast.text)
    except Exception:
        print("Toast not found.")

    print("All test steps finished.")

finally:
    time.sleep(2)
    driver.quit()
