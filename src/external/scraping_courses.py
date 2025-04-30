# scraper_scheduler.py

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def run_scraper():
    print("Starting scraping...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    driver.get("https://auasonis.jenzabarcloud.com/GENSRsC.cfm")

    wait.until(EC.presence_of_element_located((By.ID, "crsbysemester")))

    driver.execute_script("""
        let select = document.querySelector("select[name='crsbysemester_length']");
        if (select) {
            select.value = "-1";  // Show all records
            select.dispatchEvent(new Event('change'));
        }
    """)

    time.sleep(7)

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

    output_dir = "C:/Users/MSI/Desktop/Software-git/AUA-Course-Planner/src/data"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, "courses_scraped.json")

    df = pd.DataFrame(data)
    df.to_json(filename, orient="records", indent=4, force_ascii=False)

    print(f"Scraping finished and saved into '{filename}'!")

    driver.quit()

run_scraper()
