import asyncio
from playwright.async_api import async_playwright
from string_random import generate_random_string, generate_random_email, generate_random_contact_number
import random

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/medicines")
        await page.goto("http://localhost:5000/suppliers")
        for i in range(30):
            sup = {
                "name": generate_random_string(8),
                "contact_number": generate_random_contact_number(),
                "email": generate_random_email(),
                "city": generate_random_string(5)
            }
            await page.click("button.btn-primary")
            await page.wait_for_selector("#supplierModal.show")
            await page.type("#supplierModal input[name='name']", sup["name"], delay=180) 
            await page.type("#supplierModal input[name='contact_number']", sup["contact_number"], delay=180)
            await page.type("#supplierModal input[name='email']", sup["email"], delay=180)
            await page.type("#supplierModal input[name='city']", sup["city"], delay=180)
            await page.click("#supplierForm button[type='submit']")
            await page.wait_for_selector("#supplierModal", state="hidden")
            print(f"Added supplier: {sup['name']}")
            await page.wait_for_timeout(3000) 
        print("All suppliers added successfully.")
        
        
        
        await page.goto("http://localhost:5000/medicines")
        for i in range(30):
            med = {
                "name": generate_random_string(8),
                "brand": generate_random_string(5),
                "quantity": random.randint(1, 100),
                "price": round(random.uniform(10, 1000), 2),
                "expiry_date": f"{random.randint(1,12)- 1:02d}-{random.randint(1,28):02d}-{random.randint(2026, 2030)}"
            }
            await page.click("#openAddModal")  
            await page.wait_for_selector("#addModal.show")
            await page.type("#addModal input[name='name']", med["name"], delay=150)
            await page.type("#addModal input[name='brand']", med["brand"], delay=150)
            # Select a random category (excluding the first placeholder)
            category_select = await page.query_selector("#categoryDropdown")
            category_options = await category_select.query_selector_all("option")
            valid_categories = category_options[1:] if len(category_options) > 1 else category_options
            random_category = random.choice(valid_categories)
            category_value = await random_category.get_attribute("value")
            await page.select_option("#categoryDropdown", value=category_value)
            await page.type("#addModal input[name='quantity']", str(med["quantity"]), delay=150)
            await page.type("#addModal input[name='price']", str(med["price"]), delay=150)
            await page.type("#addModal input[name='expiry_date']", med["expiry_date"], delay=150)
            
            supplier_select = await page.query_selector("#addModal select[name='supplier_id']")
            options = await supplier_select.query_selector_all("option")
            # Exclude the first option if it's a placeholder
            valid_options = options[1:] if len(options) > 1 else options
            random_option = random.choice(valid_options)
            supplier_value = await random_option.get_attribute("value")
            await page.select_option("#addModal select[name='supplier_id']", value=supplier_value)
            await page.click("#addForm button[type='submit']")
            await page.wait_for_selector("#addModal", state="hidden")
            print(f"Added medicine: {med['name']}")
            await page.wait_for_timeout(2000)
        print("All medicines added successfully.")
        
        
        await page.goto("http://localhost:5000/customers")
        for i in range(30):
            customer = {
                "name": generate_random_string(8),
                "contact_number": generate_random_contact_number(),
                "email": generate_random_email()
            }
            await page.click("button.btn-primary")
            await page.wait_for_selector("#customerModal.show")
            await page.type("#customerModal input[name='name']", customer["name"], delay=180)
            await page.type("#customerModal input[name='contact_number']", customer["contact_number"], delay=180)
            await page.type("#customerModal input[name='email']", customer["email"], delay=180)
            await page.click("#customerForm button[type='submit']")
            await page.wait_for_selector("#customerModal", state="hidden")
            print(f"Added customer: {customer['name']}")
            await page.wait_for_timeout(3000)
            
        # await page.goto("http://localhost:5000/medicines")
        # await page.wait_for_selector("#openSellModal")
        # await page.click("#openSellModal")
        # await page.wait_for_selector("#sellModal.show")
        # await page.wait_for_timeout(2000)
        # customer_select = await page.query_selector("#sellModal select#customer_id")
        # customer_options = await customer_select.query_selector_all("option")
        # customer_value = await customer_options[1].get_attribute("value")
        # await customer_select.select_option(customer_value)
        # await page.wait_for_timeout(2000)
        # medicine_select = await page.query_selector("#itemsBody select[name='medicine_id']")
        # medicine_options = await medicine_select.query_selector_all("option")
        # med_value = await medicine_options[1].get_attribute("value")
        # await medicine_select.select_option(med_value)
        # await page.wait_for_timeout(2000)
        # qty_input = await page.query_selector("#itemsBody input[name='quantity']")
        # await qty_input.fill("2") 
        # await page.wait_for_timeout(2000)
        # disc_input = await page.query_selector("#itemsBody input[name='discount']")
        # await disc_input.fill("5")
        # await page.wait_for_timeout(2000)
        # await page.click("#sellModal button[type='submit']")
        # await page.wait_for_timeout(2000)
        # print("Sale submitted!")
        # await page.wait_for_selector("#sellModal.close", state="hidden")
        # await page.wait_for_timeout(5000)
        
        # # Go to sales history page and wait for table
        # await page.goto("http://localhost:5000/sales_history")
        # await page.wait_for_selector("table")
        # await page.wait_for_timeout(2000)
        # # Find and click the first 'View' button in the sales table
        # view_buttons = await page.query_selector_all("a.btn-success[title='View']")
        # await view_buttons[0].click() 
        # await page.wait_for_timeout(2000)
        # await page.wait_for_load_state("networkidle")
        # await page.wait_for_timeout(5000)
        # print("Clicked on the last sale's View button.")

        
        await browser.close()
asyncio.run(run_test())
