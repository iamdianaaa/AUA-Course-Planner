import os
import time
import schedule
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class CourseScraper:
    def __init__(self):
        self.url = "https://auasonis.jenzabarcloud.com/GENSRsC.cfm"

        script_dir = os.path.dirname(os.path.abspath(__file__))  # /src/external
        data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
        self.filename = os.path.join(data_dir, "courses_scraped.json")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created directory: {data_dir}")

        if not os.path.isfile(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("[]")
            print(f"Created new file at '{self.filename}'")

    def run(self):
        print("Starting scraping...")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        driver.get(self.url)

        wait.until(EC.presence_of_element_located((By.ID, "crsbysemester")))

        driver.execute_script("""
            let select = document.querySelector("select[name='crsbysemester_length']");
            if (select) {
                select.value = "-1";
                select.dispatchEvent(new Event('input', { bubbles: true }));
                select.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#crsbysemester tbody tr")))

        table = driver.find_element(By.ID, "crsbysemester")
        rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        data = []

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) == 12:
                course_info = {
                    "Course": columns[0].text.strip(),
                    "Section": columns[1].text.strip(),
                    "Session": columns[2].text.strip(),
                    "Credits": columns[3].text.strip(),
                    "Campus": columns[4].text.strip(),
                    "Instructor": columns[5].text.strip(),
                    "Times": columns[6].text.strip(),
                    "Taken/Seats": columns[7].text.strip(),
                    "Spaces Waiting": columns[8].text.strip(),
                    "Delivery Method": columns[9].text.strip(),
                    "Dist. Learning": columns[10].text.strip(),
                    "Location": columns[11].text.strip()
                }
                data.append(course_info)

        df = pd.DataFrame(data)
        df.to_json(self.filename, orient="records", indent=4, force_ascii=False)

        print(f"Scraping finished and saved into '{os.path.basename(self.filename)}'!")

        driver.quit()

def schedule_scraping():
    scraper = CourseScraper()
    schedule.every().day.at("14:55").do(scraper.run)

    print("Scheduler started! Waiting for the next scheduled job...")

    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_scraping()
