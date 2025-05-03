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

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_dir = os.path.join(project_root, "data", "scraped_courses")
        self.filename = os.path.join(self.save_dir, "aua_courses_by_semester.json")

        os.makedirs(self.save_dir, exist_ok=True)

        if not os.path.isfile(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("[]")
            #print(f"Created new file at '{self.filename}'")

    def run(self):
        print("Starting scraping...")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        try:
            driver.get(self.url)

            wait.until(EC.presence_of_element_located((By.ID, "crsbysemester")))

            # Change dropdown to "All"
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

            # Save to JSON
            df = pd.DataFrame(data)
            df.to_json(self.filename, orient="records", indent=4, force_ascii=False)

            print(f"Scraping completed and saved to: {self.filename}")

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            driver.quit()


def schedule_scraping():
    scraper = CourseScraper()
    schedule.every().day.at("07:20").do(scraper.run)
    print("Scheduler started! Waiting for the next run...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule_scraping()
