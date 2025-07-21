import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/medicines")
        
        suppliers = [
            {"name": "Sa", "contact_number": "10000000001", "email": "sup1@mail.com", "city": "Karachi"},
            {"name": "Sb", "contact_number": "10000000002", "email": "sup2@mail.com", "city": "Lahore"},
            {"name": "Sc", "contact_number": "10000000003", "email": "sup3@mail.com", "city": "Islamabad"},
            {"name": "Sd", "contact_number": "10000000004", "email": "sup4@mail.com", "city": "Peshawar"},
            {"name": "Se", "contact_number": "10000000005", "email": "sup5@mail.com", "city": "Quetta"},
        ]

        await page.goto("http://localhost:5000/suppliers")
        for sup in suppliers:
            await page.click("button.btn-primary")
            await page.wait_for_selector("#supplierModal.show")
            await page.type("#supplierModal input[name='name']", sup["name"], delay=150) 
            await page.type("#supplierModal input[name='contact_number']", sup["contact_number"], delay=150)
            await page.type("#supplierModal input[name='email']", sup["email"], delay=150)
            await page.type("#supplierModal input[name='city']", sup["city"], delay=150)
            await page.click("#supplierForm button[type='submit']")
            await page.wait_for_selector("#supplierModal", state="hidden")
            print(f"Added supplier: {sup['name']}")
            await page.wait_for_timeout(2000)  # 2 seconds
        print("All suppliers added successfully.")
        
        
        
    
        # Adding medicines     
        medicines = [
            {"name": "ma", "brand": "ba", "quantity": 10, "price": 100.00, "expiry_date": "2030-12-31"},
            {"name": "mb", "brand": "bb", "quantity": 20, "price": 200.00, "expiry_date": "2030-12-31"},
            {"name": "mc", "brand": "bc", "quantity": 30, "price": 300.00, "expiry_date": "2030-12-31"},
            {"name": "md", "brand": "bd", "quantity": 40, "price": 400.00, "expiry_date": "2030-12-31"},
            {"name": "me", "brand": "be", "quantity": 50, "price": 500.00, "expiry_date": "2030-12-31"},
        ]
        
        await page.goto("http://localhost:5000/medicines")
        for med in medicines:
            await page.click("#openAddModal")  # Use the actual Add Medicine button's selector
            await page.wait_for_selector("#addModal.show")  # Use the correct modal ID
            await page.wait_for_selector("#addModal input[name='name']", state="visible")
            await page.type("#addModal input[name='name']", med["name"], delay=150)
            await page.fill("#addModal input[name='brand']", med["brand"], delay=150)
            await page.select_option("#categoryDropdown", label="c1", delay=150)  # Assuming "c1" is a valid category label
            await page.fill("#addModal input[name='quantity']", str(med["quantity"]), delay=150)
            await page.fill("#addModal input[name='price']", str(med["price"]), delay=150)
            await page.fill("#addModal input[name='expiry_date']", med["expiry_date"], delay=150)
            supplier_value = await options[1].get_attribute("value") 
            await page.select_option("#addModal select[name='supplier_id']", supplier_value, delay=150)
            await page.click("#addForm button[type='submit']")
            await page.wait_for_selector("#addModal", state="hidden")
            print(f"Added medicine: {med['name']}")
            await page.wait_for_timeout(2000)
        print("All medicines added successfully.")


asyncio.run(run_test())
