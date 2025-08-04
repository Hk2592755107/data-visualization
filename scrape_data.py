import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd


async dasync def scrape_all_suppliers():
    suppliers = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/suppliers")
        await page.wait_for_selector("table")
        while True:
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            supp_table = soup.find('table')
            if supp_table:
                for row in supp_table.find('tbody').find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        supplier_row = [
                            cols[0].get_text(strip=True),
                            cols[1].get_text(strip=True),
                            cols[2].get_text(strip=True),
                            cols[3].get_text(strip=True),
                            cols[4].get_text(strip=True),
                            cols[5].get_text(strip=True),
                        ]
                        if supplier_row not in suppliers:
                            suppliers.append(supplier_row)
            next_btn = await page.query_selector('li.paginate_button.page-item.next:not(.disabled)')
            if next_btn:
                link = await next_btn.query_selector('a.page-link')
                if link:
                    await link.click()
                    await page.wait_for_timeout(600)
                else:
                    break
            else:
                break
        await browser.close()
    return suppliers

async def scrape_all_customers():
    customers = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/customers")
        await page.wait_for_selector("table")
        while True:
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cust_table = soup.find('table')
            if cust_table:
                for row in cust_table.find('tbody').find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        customer_row = [
                            cols[0].get_text(strip=True),
                            cols[1].get_text(strip=True),
                            cols[2].get_text(strip=True),
                            cols[3].get_text(strip=True),
                            cols[4].get_text(strip=True),
                        ]
                        if customer_row not in customers:
                            customers.append(customer_row)
            next_btn = await page.query_selector('li.paginate_button.page-item.next:not(.disabled)')
            if next_btn:
                link = await next_btn.query_selector('a.page-link')
                if link:
                    await link.click()
                    await page.wait_for_timeout(600)
                else:
                    break
            else:
                break
        await browser.close()
    return customers

async def scrape_all_medicines():
    medicines = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/medicines")
        await page.wait_for_selector("table")
        while True:
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            med_table = soup.find('table')
            if med_table:
                for row in med_table.find('tbody').find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 8:
                        medicine_row = [
                            cols[0].get_text(strip=True),
                            cols[1].get_text(strip=True),
                            cols[2].get_text(strip=True),
                            cols[3].get_text(strip=True),
                            cols[4].get_text(strip=True),
                            cols[5].get_text(strip=True),
                            cols[6].get_text(strip=True),
                            cols[7].get_text(strip=True),
                            cols[8].get_text(strip=True),
                        ]
                        if medicine_row not in medicines:
                            medicines.append(medicine_row)
            next_btn = await page.query_selector('li.paginate_button.page-item.next:not(.disabled)')
            if next_btn:
                link = await next_btn.query_selector('a.page-link')
                if link:
                    await link.click()
                    await page.wait_for_timeout(600)
                else:
                    break
            else:
                break
        await browser.close()
    return medicines


def save_suppliers_to_excel(suppliers, file_path="suppliers_list.xlsx"):
    df = pd.DataFrame(suppliers, columns=["ID", "Name", "Contact_Number", "Email", "City", "Created_At"])
    df.to_excel(file_path, index=False)
    print(f"Saved {len(suppliers)} suppliers to {file_path}")

def save_customers_to_excel(customers, file_path="customers_list.xlsx"):
    df = pd.DataFrame(customers, columns=["ID", "Name", "Contact_Number", "Email", "Created_At"])
    df.to_excel(file_path, index=False)
    print(f"Saved {len(customers)} customers to {file_path}")

def save_medicines_to_excel(medicines, file_path="medicines_list.xlsx"):
    df = pd.DataFrame(medicines, columns=["ID", "Name", "Brand", "Category", "Quantity", "Price", "Expiry_Date", "Supplier_ID", "Created_At"])
    df.to_excel(file_path, index=False)
    print(f"Saved {len(medicines)} medicines to {file_path}")


if __name__ == "__main__":
    suppliers = asyncio.run(scrape_all_suppliers())
    save_suppliers_to_excel(suppliers)
    customers = asyncio.run(scrape_all_customers())
    save_customers_to_excel(customers)
    medicines = asyncio.run(scrape_all_medicines())
    save_medicines_to_excel(medicines)