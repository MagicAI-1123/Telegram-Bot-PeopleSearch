from aiogram import F, Router
from aiogram.types import Message
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
from datetime import datetime
from selenium.common.exceptions import TimeoutException

target_url_email = os.getenv("TARGET_URL_Email")
target_url_phone = os.getenv("TARGET_URL_Phone")

input_value = ""
input_type = ""

class WebScraper:
    def __init__(self):  
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 20)  # Reduced from 20 to 10 seconds
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def initialize_driver(self):  
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')  
        # chrome_options.add_argument("--user-data-dir=C:/Info_SeleniumChromeProfile")
        
        # chrome_options.add_argument("--headless=new")  # Modern headless mode
        
        # Add performance-focused options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-browser-side-navigation')
        
        # More aggressive content blocking
        chrome_prefs = {
            "profile.default_content_setting_values": {
                "images": 2,
                "media_stream": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "auto_select_certificate": 2,
                "fullscreen": 2,
                "mouselock": 2,
                "mixed_script": 2,
                "media_stream_mic": 2,
                "media_stream_camera": 2,
                "protocol_handlers": 2,
                "ppapi_broker": 2,
                "automatic_downloads": 2,
                "midi_sysex": 2,
                "push_messaging": 2,
                "ssl_cert_decisions": 2,
                "metro_switch_to_desktop": 2,
                "protected_media_identifier": 2,
                "app_banner": 2,
                "site_engagement": 2,
                "durable_storage": 2
            }
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        webdriver_service = Service(ChromeDriverManager().install())  

        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)  
        driver.maximize_window()
        return driver
    
    # def take_screenshot(self, step_name):
    #     """Helper method to take and save screenshots"""
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = f"{self.screenshot_dir}/{step_name}_{timestamp}.png"
    #     try:
    #         self.driver.save_screenshot(filename)
    #         print(f"Screenshot saved: {filename}")
    #     except Exception as e:
    #         print(f"Failed to take screenshot: {str(e)}")
    
    
    async def scrape_website(self): 
        try:
            self.driver.get(target_url_email if input_type == "email" else target_url_phone)
            time.sleep(3)
            
            try:
                modal_dialog = self.driver.find_element(By.CLASS_NAME, "modal-dialog")
                modal_dialog.find_element(By.CLASS_NAME, "btn btn-primary").click()
            except Exception as e:
                print("No modal dialog found, continuing...")

            
            if input_type == "email":
                self.input_email()
            elif input_type == "phone":
                self.input_phone()
            time.sleep(1)
            
            submit_button = self.wait.until(EC.presence_of_element_located((By.ID, "btn")))
            submit_button.click()
            
            response_element = self.wait.until(EC.presence_of_element_located((By.ID, "response")))
            print("self.result: ", response_element.text)
            
            time.sleep(3)
            
            response_element = self.driver.find_element(By.ID, "response")
            print("self.result: ", response_element.text)
            
            self.wait.until(lambda driver: 
                "hold on" not in driver.find_element(By.ID, "response").text.lower() and
                driver.find_element(By.ID, "response").text.strip() != ""
            )
            
            response_element = self.driver.find_element(By.ID, "response")
            response_text = response_element.text
            
            print("response_text: ", response_text)
            
            # Updated parsing logic to handle both email and phone responses
            if "Skype Account Name Country" in response_text:
                results = []
                
                response_element = self.driver.find_element(By.ID, "response")
                response_text = response_element.text
                
                table_element = self.driver.find_element(By.TAG_NAME, "tbody")
                rows = table_element.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        skype_id = cells[1].text.strip()
                        name = cells[2].text.strip()
                        country = cells[3].text.strip()
                    except Exception as e:
                        print(e)
                        continue
                    
                    results.append({
                        'skype_id': skype_id,
                        'name': name,
                        'country': country
                    })
                
                return results
            
            return None
        except Exception as e:
            print(e)
        finally:
            # Ensure driver is closed
            self.close_driver()

    def input_email(self):
        email_element = self.wait.until(EC.presence_of_element_located((By.ID, "PIN_1")))
        email_element.clear()
        email_element.send_keys(input_value)
        
    def input_phone(self):
        phone_element = self.wait.until(EC.presence_of_element_located((By.ID, "PIN_1")))
        phone_element.clear()
        phone_element.send_keys(input_value)

    def close_driver(self):  
        try:
            self.driver.quit()
        except Exception as e:
            print(e)


async def run_scraper(_input_value, _input_type):
    global input_value, input_type
    
    input_value = _input_value
    input_type = _input_type
    
    scraper = WebScraper()
    result = await scraper.scrape_website()
    return result


skype_router = Router()

@skype_router.message(F.text.startswith("/skype"))
async def handle_skype_command(message: Message):
    """Handles the /skype command."""
    skype_input = message.text.split("/skype ")[1]  # Extract the full name from the message
    parts = skype_input.split()
    if len(parts) < 2:
        await message.answer("Invalid input. Please provide email or phone.")
        return
    input_value = parts[0]
    input_type = parts[1]
    print("---------", input_value, input_type)
    
    result = await run_scraper(input_value, input_type)
    print("result: ", result)
    
    # Save the result to a text file
    filename = f"{input_value}_{input_type}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"Result saved to {filename}")
    await message.answer(result)