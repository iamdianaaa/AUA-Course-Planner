import os
import json
import fitz  # PyMuPDF
import requests
from io import BytesIO
from PIL import Image
import pytesseract
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup

class DegreeRequirementsExtractor:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.output_path = os.path.join(base_dir, "data", "requirements", "degree_requirements.json")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def save_entry(self, slug, entry):
        # Step 1: Create file if doesn't exist, with valid structure
        if not os.path.exists(self.output_path) or os.stat(self.output_path).st_size == 0:
            all_data = {}
        else:
            try:
                with open(self.output_path, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping save: Existing JSON is corrupt or empty.")
                all_data = {}

        all_data[slug] = entry
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

    def extract_from_pdf_url(self, slug, url, program_name=None):
        try:
            response = requests.get(url)
            response.raise_for_status()

            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            doc = fitz.open(tmp_path)
            raw_text = "\n".join(page.get_text() for page in doc)
            doc.close()
            os.remove(tmp_path)

            entry = {
                "program": program_name or slug.replace("_", " ").title(),
                "raw_text": raw_text
            }
            self.save_entry(slug, entry)

        except Exception as e:
            print(f"Error extracting {slug} from PDF: {e}")

    def extract_from_image_links(self, url_map):
        for slug, url in url_map.items():
            try:
                response = requests.get(url)
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                raw_text = pytesseract.image_to_string(image)

                entry = {
                    "program": slug.replace("_", " ").title(),
                    "raw_text": raw_text
                }
                self.save_entry(slug, entry)

            except Exception as e:
                print(f"Failed to extract from image link {slug}: {e}")




if __name__ == "__main__":
    extractor = DegreeRequirementsExtractor()

    #  PDF sources
    pdf_links = {
        "ba_business": "https://cbe.aua.am/files/2024/12/BA-in-Business-Degree-Requirements.pdf",
        "ba_economics": "https://baec.aua.am/files/2024/04/EC-Current-Degree-Requirements.pdf",
        "bs_c_computer-science": "https://cse.aua.am/files/2024/08/BS-in-CS-Degree-Requirements-2024.pdf",
        "bs_data_science": "https://cse.aua.am/files/2024/09/Bachelor-of-Science-in-Data-Science-Degree-Requirements2024.pdf",
        "bs_engineering_sciences": "https://cse.aua.am/files/2023/07/Bachelor-of-Science-in-Engineering-Sciences-Degree-Requirements-2.pdf",
        "bs_environmental_science": "https://cse.aua.am/files/2024/08/BSESS-Curriculum-Map-Aug-2024.pdf",
        "bs_nursing": "https://chs.aua.am/files/2024/01/BSN-Curriculum-map-2024.pdf",
        "ms_cis":"https://cse.aua.am/files/2023/10/MS-in-CIS-Degree-Requirements.pdf",
        "ms_iesm":"https://cse.aua.am/files/2024/01/IESM-DA_Degree-Requirements.pdf"
    }

    for slug, url in pdf_links.items():
        extractor.extract_from_pdf_url(slug, url)

    # OCR from local images
    image_links = {
        "Master of Arts in International Relations and Diplomacy (MAIRD)": "https://psia.aua.am/files/2024/08/MAIRD_Course_Sequence-1.png",
        "Master of Public Affairs (MPA)": "https://psia.aua.am/files/2024/08/MPA_Course_Sequence-1.png",
        "mba_structure_1": "https://cbe.aua.am/files/2025/01/Program-Structure-1-1024x579.png",
        "mba_structure_2": "https://cbe.aua.am/files/2025/01/MBA-Program-Structure-2.png",
        "bachelor_degree_political_science": "https://bapg.aua.am/files/2022/09/PG-Degree-and-Graduation-RequirementsUpdated.jpg"
    }

    extractor.extract_from_image_links(image_links)


