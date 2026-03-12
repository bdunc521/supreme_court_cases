#Program as on script. Also available in the code.ipynb file

import pandas as pd 
import requests
import re
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import time

def main():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/pdf,application/xhtml+xml"
    }

    base_url = "https://www.supremecourt.gov/opinions/slipopinion/"

    cases = []
    for term in range(18, 24):

        url = f"{base_url}{term}"
        print("Scraping:", url)

        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if href.endswith(".pdf"):

                pdf_url = "https://www.supremecourt.gov" + href
                row = link.find_parent("tr")

                if row:

                    cols = row.find_all("td")

                    if len(cols) >= 4:

                        date = cols[1].get_text(strip=True)
                        docket = cols[2].get_text(strip=True)
                        case_name = cols[3].get_text(strip=True)
                        justice = cols[4].get_text(strip=True)

                        cases.append({
                            "date": date,
                            "docket": docket,
                            "case_name": case_name,
                            "justice": justice,
                            "pdf_url": pdf_url
                        })

    data = []

    for i, case in enumerate(cases):

        pdf_url = case["pdf_url"]

        print(f"Processing {i+1}/{len(cases)}")

        try:

            response = session.get(pdf_url, headers=headers)

            if "application/pdf" not in response.headers.get("Content-Type", ""):
                print("Skipped:", pdf_url)
                continue

            reader = PdfReader(BytesIO(response.content))

            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t

            word_count = len(text.split())
            page_count = len(reader.pages)
            dissent_count = text.lower().count("dissent")
            concurrence_count = text.lower().count("concur")
            first_amend_count = text.lower().count("first amendment")
            fourth_amend_count = text.lower().count("fourth amendment")
            fifth_amend_count = text.lower().count("fifth amendment")
            sixth_amend_count = text.lower().count("sixth amendment")
            eigth_amend_count = text.lower().count("eighth amendment")

            data.append({
                "date": case["date"],
                "docket": case["docket"],
                "case_name": case["case_name"],
                "justice": case["justice"],
                "pdf_url": pdf_url,
                "word_count": word_count,
                "page_count": page_count,
                "dissent_mentions": dissent_count,
                "concurrence_mentions": concurrence_count,
                "first_amend_mentions": first_amend_count,
                "fourth_amend_mentions": fourth_amend_count,
                "fifth_amend_mentions": fifth_amend_count,
                "sixth_amend_mentions": sixth_amend_count,
                "eigth_amend_mentions": eigth_amend_count
            })

            #time.sleep(1)

        except Exception as e:
            print("Error:", pdf_url)
            print(e)


# STEP 3: Create dataset
    df = pd.DataFrame(data)

if __name__ == "__main__":
    main()
