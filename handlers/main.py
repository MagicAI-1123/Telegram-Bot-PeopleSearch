import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
import re
import json

import asyncio

def extract_length(content: str):
    # Regular expression to find numbers
    numbers = re.findall(r'\d+', content)

    # Assuming there is at least one number, get the first one
    number = numbers[0] if numbers else 0
    return number

class WebScraper:
    # Create a WebScraper instance
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 30)  # Added explicit wait
        self.reports = []

    # Init the WebScraper instance
    def initialize_driver(self):
        # command = [
        # "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        # f"--user-data-dir={profile}",
        # "--remote-debugging-port=9222"
        # ]
        # subprocess.Popen(command)
    
        chrome_options = Options()
        # chrome_options.add_argument("--headless")

        chrome_options.add_argument("--user-data-dir=C:/SeleniumChromeProfile")
        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        # driver.maximize_window()
        return driver
    
    
##############BuilderTrend################
    # Scrape the buildertrend website
    async def scrape_buildertrend_website(self, url):
        self.driver.get(url)
        time.sleep(3)
        
        # await self.scrape_each_person(url)
        # return
        self.driver.execute_script("document.getElementById('header-login').click()")
        
        try:
            # try:
            #     email_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'email')))
            #     email_element.clear()
            #     email_element.send_keys(self.email)
                
            #     password_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            #     password_element.clear()
            #     password_element.send_keys(self.password)
                
            #     submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            #     submit_button.click()

            # except Exception as e:
            #     print("no logged in form found")
            
            # print("password passed")
            
            # try:
            #     email_element = self.wait.until(EC.presence_of_element_located((By.ID, 'dont-show-check')))
            #     self.driver.execute_script("document.getElementById('dont-show-check').click()")            
            #     print("clicked squaredFour")
            # except Exception as e:
            #     print("no dont-show-check found")
                
            
            firstName_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'firstName')))
            firstName_element.clear()
            firstName_element.send_keys("Elliot")
            
            lastName_element = self.wait.until(EC.presence_of_element_located((By.NAME, 'lastName')))
            lastName_element.clear()
            lastName_element.send_keys("Bogod")

            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            submit_button.click()
            
            people_list = []
            
            try:
                person_search_results = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "person-search-result")))
                for person in person_search_results:
                    print("person found")
                    link = person.find_element(By.TAG_NAME, 'a')
                    href = link.get_attribute('href')
                    print(f"Person link: {href}")
                    people_list.append(href)
            except Exception as e:
                print("no person search results found")
                print(e)
                
            for link in people_list:
                await self.scrape_each_person(link)
                break
        except Exception as e:
            import traceback
            print("An error occurred:", str(e))
            traceback.print_exc()  # This will print the stack trace to the console

    async def scrape_each_person(self, link):
        self.driver.get(link)
        time.sleep(3)
        
        await self.get_contact_information()
        # await self.get_personal_information()
        # await self.get_business_information()
        
        time.sleep(3)

    async def get_contact_information(self):
        try:
            phone_section = self.driver.find_element(By.CLASS_NAME, 'phones-subsection')  
            phone_items = phone_section.find_elements(By.CLASS_NAME, 'phone-subsection-item')  

            for item in phone_items:  
                phone_number = item.find_element(By.CLASS_NAME, 'phone-number').text  
                line_type = item.find_element(By.XPATH, ".//p[contains(text(), 'Line Type')]/following-sibling::p/span").text  
                carrier_location = item.find_element(By.XPATH, ".//p[contains(text(), 'Carrier Location')]/following-sibling::p/span").text  
                
                print(f'Phone Number: {phone_number}, Line Type: {line_type}, Carrier Location: {carrier_location}')  

            # Extract email addresses  
            email_section = self.driver.find_element(By.CLASS_NAME, 'emails-subsection')  
            email_items = email_section.find_elements(By.CLASS_NAME, 'section-table-header')  

            for email_item in email_items:  
                email_address = email_item.find_element(By.TAG_NAME, 'h5').text  
                print(f'Email Address: {email_address}') 
        except Exception as e:
            print("no CONTACT INFORMATION section found")
            print(e)

    async def get_personal_information(self):
        relative_cards = self.driver.find_elements(By.CLASS_NAME, 'relative-card')  

        for card in relative_cards:  
            try:  
                # Extract the person's name  
                name = card.find_element(By.TAG_NAME, 'h3').text  
                
                # Extract location  
                location_label = card.find_element(By.XPATH, ".//p[contains(text(), 'Location')]")  
                location = location_label.find_element(By.XPATH, "following-sibling::p").text  

                # Attempt to extract age, if exists  
                try:  
                    age_label = card.find_element(By.XPATH, ".//p[contains(text(), 'Age')]")  
                    age = age_label.find_element(By.XPATH, "following-sibling::p").text  
                except:  
                    age = "Not available"  

                # Print the extracted details  
                print(f"Name: {name}, Age: {age}, Location: {location}")  

            except Exception as e:  
                # Print any errors that occur  
                print("An error occurred:", e) 

    async def get_business_information(self):
        section_classes = ['corporate-filings-section', 'business-affiliations-section']  

        for section_class in section_classes:  
            print(f"Extracting data for section: {section_class}")  
            
            try:  
                # Find each section by its class  
                section = self.driver.find_element(By.CLASS_NAME, section_class)  
                
                # Find all tables within the section  
                tables = section.find_elements(By.TAG_NAME, 'table')  

                # Extract data from each table in the section  
                self.extract_table_data(tables)  
            
            except Exception as e:  
                print(f"Error extracting data from section {section_class}: {e}")

    async def extract_table_data(self, tables):  
        for table in tables:  
            rows = table.find_elements(By.TAG_NAME, 'tr')  
            for row in rows:  
                cells = row.find_elements(By.TAG_NAME, 'td')  
                if len(cells) >= 2:  
                    key = cells[0].text.strip()  
                    value = cells[1].text.strip()  
                    print(f"{key}: {value}")  
        
    async def close_driver(self):
        self.driver.quit()

async def run_scraper():
    scraper = WebScraper("Ceo@m2echicago.com", "Var+(n42421799)")
    # await scraper.scrape_buildertrend_website("https://www.truthfinder.com/")
    await scraper.scrape_buildertrend_website("https://www.truthfinder.com/dashboard/reports/6a777832-5521-47a9-9a22-a75cba0d1467")
    time.sleep(3)
    await scraper.close_driver()
    
asyncio.run(run_scraper())