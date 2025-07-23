import asyncio
import time
import random
import csv
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from string_random import generate_random_string, generate_random_email, generate_random_contact_number
from load_measurement import measure_latency, LATENCY_LOG, export_latency_to_csv


async def run_test_and_measure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        page = await browser.new_page()
        start = time.time()
        await page.goto("http://localhost:5000/medicines")
        await page.goto("http://localhost:5000/suppliers")
        for _ in range(10):
            sup = {
                "name": generate_random_string(8),
                "contact_number": generate_random_contact_number(),
                "email": generate_random_email(),
                "city": generate_random_string(5)
            }
            await page.click("button.btn-primary")
            await page.wait_for_selector("#supplierModal.show")
            await page.type("#supplierModal input[name='name']", sup["name"], delay=150)
            await page.type("#supplierModal input[name='contact_number']", sup["contact_number"], delay=150)
            await page.type("#supplierModal input[name='email']", sup["email"], delay=150)
            await page.type("#supplierModal input[name='city']", sup["city"], delay=150)
            await page.click("#supplierForm button[type='submit']")
            await page.wait_for_selector("#supplierModal", state="hidden")
            measure_latency("http://localhost:5000/suppliers")
        print("Suppliers added.")
        total_latency = sum(entry['response_time'] for entry in LATENCY_LOG if entry['url'] == "http://localhost:5000/suppliers")
        print(f"Total latency for suppliers: {total_latency:.3f}s")


        await page.goto("http://localhost:5000/medicines")
        for _ in range(10):
            med = {
                "name": generate_random_string(8),
                "brand": generate_random_string(5),
                "quantity": random.randint(1, 100),
                "price": round(random.uniform(10, 1000), 2),
                "expiry_date": (datetime.today() + timedelta(days=random.randint(365, 1460))).strftime("%m-%d-%Y")
            }
            await page.click("#openAddModal")
            await page.wait_for_selector("#addModal.show")
            await page.type("#addModal input[name='name']", med["name"], delay=150)
            await page.type("#addModal input[name='brand']", med["brand"], delay=150)

            category_select = await page.query_selector("#categoryDropdown")
            category_options = await category_select.query_selector_all("option")
            valid_categories = category_options[1:]
            random_category = random.choice(valid_categories)
            category_value = await random_category.get_attribute("value")
            await page.select_option("#categoryDropdown", value=category_value)

            await page.type("#addModal input[name='quantity']", str(med["quantity"]), delay=150)
            await page.type("#addModal input[name='price']", str(med["price"]), delay=150)
            await page.type("#addModal input[name='expiry_date']", med["expiry_date"], delay=150)

            supplier_select = await page.query_selector("#addModal select[name='supplier_id']")
            options = await supplier_select.query_selector_all("option")
            valid_options = options[1:] if len(options) > 1 else options
            random_option = random.choice(valid_options)
            supplier_value = await random_option.get_attribute("value")
            await page.select_option("#addModal select[name='supplier_id']", value=supplier_value)

            await page.click("#addForm button[type='submit']")
            await page.wait_for_selector("#addModal", state="hidden")
            measure_latency("http://localhost:5000/medicines")
        print("Medicines added.")
        total_latency = sum(entry['response_time'] for entry in LATENCY_LOG if entry['url'] == "http://localhost:5000/medicines")
        print(f"Total latency for medicines: {total_latency:.3f}s")
        

        await page.goto("http://localhost:5000/customers")
        for _ in range(10):
            customer = {
                "name": generate_random_string(8),
                "contact_number": generate_random_contact_number(),
                "email": generate_random_email()
            }
            await page.click("button.btn-primary")
            await page.wait_for_selector("#customerModal.show")
            await page.type("#customerModal input[name='name']", customer["name"], delay = 150)
            await page.type("#customerModal input[name='contact_number']", customer["contact_number"], delay = 150)
            await page.type("#customerModal input[name='email']", customer["email"], delay = 150)
            await page.click("#customerForm button[type='submit']")
            await page.wait_for_selector("#customerModal", state="hidden")
            measure_latency("http://localhost:5000/customers")
        print("Customers added.")
        total_latency = sum(entry['response_time'] for entry in LATENCY_LOG if entry['url'] == "http://localhost:5000/customers")
        print(f"Total latency for customers: {total_latency:.3f}s")
        
        
        await page.goto("http://localhost:5000/medicines")
        await page.click("#openSellModal")
        await page.wait_for_selector("#sellModal.show")
        await page.wait_for_timeout(2000)
        customer_select = await page.query_selector("#customer_id")
        customer_options = await customer_select.query_selector_all("option")
        valid_customers = customer_options[1:]
        random_customers = random.choice(valid_customers)
        customer_value = await random_customers.get_attribute("value")
        await customer_select.select_option(customer_value)
        await page.wait_for_timeout(2000)
        medicine_select = await page.query_selector("#itemsBody select[name='medicine_id']")
        medicine_options = await medicine_select.query_selector_all("option")
        valid_medicines = medicine_options[1:]
        random_medicines = random.choice(valid_medicines)
        medicines_value = await random_medicines.get_attribute("value")
        await medicine_select.select_option(medicines_value)
        await page.wait_for_timeout(2000)
        qty_input = await page.query_selector("#itemsBody input[name='quantity']")
        qty_value = random.randint(5,10)
        await qty_input.type(str(qty_value), delay = 150) 
        await page.wait_for_timeout(2000)
        disc_input = await page.query_selector("#itemsBody input[name='discount']")
        disc_value = random.randint(0,3)
        await disc_input.type(str(disc_value) + ".", delay = 150)
        await page.wait_for_timeout(2000)
        await page.click("#sellModal button[type='submit']")
        print("Sale submitted!")
        await page.wait_for_timeout(5000)
        await page.click("#sellModal .btn-close")
        await page.wait_for_selector("#sellModal", state="hidden")
        await page.wait_for_timeout(3000)


if __name__ == "__main__":
    print("Starting data load and latency measurement...")
    asyncio.run(run_test_and_measure())
    export_latency_to_csv()
