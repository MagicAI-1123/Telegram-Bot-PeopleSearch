from aiogram import F, Router
from aiogram.types import Message
import requests
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import asyncio
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  
from selenium.webdriver.common.keys import Keys  

target_url = os.getenv("TARGET_URL")

class WebScraper:
    def __init__(self, first_name, last_name, state_name):  
        self.first_name = first_name
        self.last_name = last_name
        self.state_name = state_name
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 100)  # Added explicit wait
        self.result = ""
    def initialize_driver(self):  
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')  

        webdriver_service = Service(ChromeDriverManager().install())  

        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)  
        driver.maximize_window()
        return driver
    
    def save_to_file(self, result, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)  

        data = []  
        
        if os.path.exists(filename):  
            with open(filename, 'r', encoding='utf-8') as file:  
                data = json.load(file)  
        data.append(result)  
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)    
        print(f"Saved data to {filename}")

    async def scrape_website(self): 
        self.driver.get(target_url)
        time.sleep(3)
        # sign in
        await self.sign_in()
        # search
        
        await self.goto_name_search()

        # await self.scrape_person_detail()
        # return self.result
        
        person_link_list = await self.input_full_name()
        print("person_link_list: ", person_link_list)
        for person_link in person_link_list:
            await self.scrape_person_detail(person_link)
            print("self.result: ", self.result)
            return self.result

    async def goto_name_search(self):
        self.driver.get("https://members.infotracer.com/customer/index?name=people")
        # self.driver.get("https://members.infotracer.com/customer/renderReport?id=671aba7783cad1d14408c372")

    async def sign_in(self):
        try:
            # cookie_button = self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            # cookie_button.click()
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_input.clear()
            email_input.send_keys(os.getenv("EMAIL"))

            password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_input.clear()
            password_input.send_keys(os.getenv("PASSWORD"))

            sign_in_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            sign_in_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)
            
    async def input_full_name(self):
        try:
            time.sleep(3)
            self.driver.execute_script("document.getElementById('fcra-agree').click()")
            time.sleep(3)
        except Exception as e:
            print("no fcra-agree button found:", str(e))
            pass
        
        first_name_input = self.wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        first_name_input.clear()
        first_name_input.send_keys(self.first_name)

        last_name_input = self.wait.until(EC.presence_of_element_located((By.ID, "lastName")))
        last_name_input.clear()
        last_name_input.send_keys(self.last_name)        
        
        state_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "state"))))
        state_dropdown.select_by_visible_text(self.state_name)
        self.driver.execute_script("""document.querySelectorAll('[type="submit"]')[0].click()""")

        time.sleep(2)
        self.driver.execute_script("document.getElementsByClassName('form-btn lbox-btn-agree fcra-agree')[1].click()")
        time.sleep(2)

        person_list_table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        person_list_items = person_list_table.find_elements(By.TAG_NAME, "a")
        person_link_list = []
        for person_list_item in person_list_items:
            person_detail_url = person_list_item.get_attribute("href")
            person_link_list.append(person_detail_url)

        return person_link_list
        
    async def scrape_person_detail(self, person_link):
    # async def scrape_person_detail(self):

        # try:
        #     time.sleep(3)
        #     self.driver.execute_script("document.getElementById('fcra-agree').click()")
        #     time.sleep(3)
        # except Exception as e:
        #     print("no fcra-agree button found:", str(e))
        #     pass


        self.driver.get(person_link)
        time.sleep(10)
        try:
            person_detail_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r2-person")))
            try:
                name = person_detail_element.find_element(By.CLASS_NAME, "title").text
                self.result += f"name: {name}\n"
                print(name)
            except Exception as e:
                print(f"Error getting name: {str(e)}")
                name = "N/A"
        except Exception as e:
            print(f"Error getting person details: {str(e)}")

        try:
            rows = person_detail_element.find_elements(By.CLASS_NAME, "row")
            for row in rows:
                try:
                    print(row.text)
                    self.result += f"{row.text}\n"
                except Exception as e:
                    print(f"Error printing row text: {str(e)}")
        except Exception as e:
            print(f"Error getting rows: {str(e)}")
        
        try:
            address_rows = self.driver.find_elements(By.CLASS_NAME, "r2-address")
            for address_row in address_rows:
                address = "N/A"
                date = "N/A"
                try:
                    address = address_row.find_elements(By.CLASS_NAME, "r2-ai-li")[0].text
                except Exception as e:
                    print(f"Error getting address: {str(e)}")
                
                try:
                    date = address_row.find_elements(By.CLASS_NAME, "r2-ai-li")[1].text
                except Exception as e:
                    print(f"Error getting date: {str(e)}")
                
                print("address, date", address, date)
                self.result += f"address: {address}, date: {date}\n"
        except Exception as e:
            print(f"Error processing address rows: {str(e)}")
        
        try:
            phone_table = self.driver.find_element(By.ID, "phone_numbers")
            phone_rows = phone_table.find_elements(By.TAG_NAME, "tr")
            for phone_row in phone_rows:
                phone_number = "N/A"
                line_type = "N/A"
                date_reported = "N/A"
                try:
                    phone_number = phone_row.find_elements(By.TAG_NAME, "td")[1].text
                except Exception as e:
                    print(f"Error getting phone number: {str(e)}")
                try:
                    line_type = phone_row.find_elements(By.TAG_NAME, "td")[2].text
                except Exception as e:
                    print(f"Error getting line type: {str(e)}")
                try:
                    date_reported = phone_row.find_elements(By.TAG_NAME, "td")[3].text
                except Exception as e:
                    print(f"Error getting date reported: {str(e)}")
                print("phone_number, line_type, date_reported", phone_number, line_type, date_reported)
                self.result += f"phone_number: {phone_number}, line_type: {line_type}, date_reported: {date_reported}\n"
        except Exception as e:
            print(f"Error processing phone table: {str(e)}")

        try:
            email_table = self.driver.find_element(By.ID, "email_addresses")
            email_rows = email_table.find_elements(By.TAG_NAME, "tr")
            for email_row in email_rows:
                name = "N/A"
                address = "N/A"
                ip_address = "N/A"
                email_address = "N/A"
                date_reported = "N/A"
                try:
                    name = email_row.find_elements(By.TAG_NAME, "td")[1].text
                except Exception as e:
                    print(f"Error getting email name: {str(e)}")
                try:
                    address = email_row.find_elements(By.TAG_NAME, "td")[2].text
                except Exception as e:
                    print(f"Error getting email address: {str(e)}")
                try:
                    ip_address = email_row.find_elements(By.TAG_NAME, "td")[3].text
                except Exception as e:
                    print(f"Error getting IP address: {str(e)}")
                try:
                    email_address = email_row.find_elements(By.TAG_NAME, "td")[4].text
                except Exception as e:
                    print(f"Error getting email address: {str(e)}")
                try:
                    date_reported = email_row.find_elements(By.TAG_NAME, "td")[5].text
                except Exception as e:
                    print(f"Error getting email date reported: {str(e)}")
                print("name, address, ip_address, email_address, date_reported", name, address, ip_address, email_address, date_reported)
                self.result += f"name: {name}, address: {address}, ip_address: {ip_address}, email_address: {email_address}, date_reported: {date_reported}\n"
        except Exception as e:
            print(f"Error processing email table: {str(e)}")

        try:
            marriage_tables = self.driver.find_element(By.ID, "section-vital_marriage").find_elements(By.CLASS_NAME, "r2-data")
            for marriage_table in marriage_tables:
                try:
                    title = marriage_table.find_element(By.TAG_NAME, "h3").text
                    self.result += f"title: {title}\n"
                    print("title", title)
                except Exception as e:
                    print(f"Error getting marriage title: {str(e)}")
                    title = "N/A"
                try:
                    marriage_rows = marriage_table.find_elements(By.TAG_NAME, "tr")
                    for marriage_row in marriage_rows:
                        key = "N/A"
                        value = "N/A"
                        try:
                            key = marriage_row.find_elements(By.TAG_NAME, "td")[0].text
                        except Exception as e:
                            print(f"Error getting marriage key: {str(e)}")
                        try:
                            value = marriage_row.find_elements(By.TAG_NAME, "td")[1].text
                        except Exception as e:
                            print(f"Error getting marriage value: {str(e)}")
                        print("key, value", key, value)
                        self.result += f"key: {key}, value: {value}\n"
                except Exception as e:
                    print(f"Error processing marriage rows: {str(e)}")
        except Exception as e:
            print(f"Error processing marriage section: {str(e)}")

        try:
            # license_tables = self.driver.find_element(By.ID, "section-professional_licenses").find_elements(By.CLASS_NAME, "accordion2 m-tb-m")
            license_tables = self.driver.execute_script("""return document.getElementById("section-professional_licenses").getElementsByClassName('accordion2 m-tb-m')""")
            for license_table in license_tables:
                print("here")
                try:
                    title_element = license_table.find_element(By.CLASS_NAME, "accordion2-header")
                    title = title_element.text
                    print("title", title)
                    self.result += f"title: {title}\n"
                    # Use JavaScript to click the element, bypassing potential overlays
                    self.driver.execute_script("arguments[0].click();", title_element)
                    # Wait for any animations or overlays to disappear
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "accordion2-header"))
                    )
                    time.sleep(1)
                except Exception as e:
                    print(f"Error getting license title: {str(e)}")
                    title = "N/A"
                try:
                    license_rows = license_table.find_elements(By.TAG_NAME, "tr")
                    for license_row in license_rows:
                        key = "N/A"
                        value = "N/A"
                        try:
                            key = license_row.find_elements(By.TAG_NAME, "td")[0].text
                        except Exception as e:
                            print(f"Error getting license key: {str(e)}")
                        try:
                            value = license_row.find_elements(By.TAG_NAME, "td")[1].text
                        except Exception as e:
                            print(f"Error getting license value: {str(e)}")
                        print("key, value", key, value)
                        self.result += f"key: {key}, value: {value}\n"
                except Exception as e:
                    print(f"Error processing license rows: {str(e)}")
        except Exception as e:
            print(f"Error processing license section: {str(e)}")

    def close_driver(self):  
        try:
            self.driver.quit()  
        except Exception as e:
            print(e)
            
state_name = "California"

async def run_scraper(first_name, last_name, state_name):
    scraper = WebScraper(first_name, last_name, state_name)
    return await scraper.scrape_website()

fullname_router = Router()

@fullname_router.message(F.text.startswith("/fullname"))
async def handle_fullname_command(message: Message):
    """Handles the /fullname command."""
    fullname = message.text.split("/fullname ")[1]  # Extract the full name from the message
    parts = fullname.split()
    if len(parts) < 3:
        await message.answer("Invalid input. Please provide first name, last name, and state name.")
        return
    first_name = parts[0]
    last_name = parts[1]
    state_name = " ".join(parts[2:])
    print("---------", first_name, last_name, state_name)
    
    result = await run_scraper(first_name, last_name, state_name)
    print("result: ", result)
    
    # Save the result to a text file
    filename = f"{first_name}_{last_name}_{state_name}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"Result saved to {filename}")
    await message.answer(f"Result saved to {filename}")