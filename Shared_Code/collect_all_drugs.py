from bs4 import BeautifulSoup
import requests
from lxml import etree
import os
import csv


def scrape_drug_names():
    base_url = "https://www.goodrx.com/drugs/"
    headers = {
        'authority': 'www.goodrx.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_pxhd=GEERJ-9uhgtcjedaZzxggOTe9hCDMOIFVhoGbqMz4sMTBCosTuRvvZD1AL/MokPaNUvmFtJg1ul16srHmUWfWw==:CPfZq1v3Y3AxJ5pJ7JyWNnoX/jX9rwVKt5tGYlpAxkxM0daWhdEXQ0gotVZpJ3EnGrh3OXrF1MWASVRcrj08hEDdlTn2xHY6N7pJK4tGvaM=; grx_unique_id=9f979cedce264f0fbb76e858c299501f; optimizelyEndUserId=9f979cedce264f0fbb76e858c299501f; grx_visit_start=1689705210; grx_sa=false; pxcts=97f55a97-2599-11ee-8ce8-486746674a73; _pxvid=97a67fcd-2599-11ee-8059-f4c4766508d8; _px2=eyJ1IjoiOTdhNjdhNmItMjU5OS0xMWVlLTgwNTktNzY2NzUzNjc2NzZlIiwidiI6Ijk3YTY3ZmNkLTI1OTktMTFlZS04MDU5LWY0YzQ3NjY1MDhkOCIsInQiOjE1NjE1MDcyMDAwMDAsImgiOiIzYTk0YWU4MmYzMzQ0MmJjZmUxZjg1YzllNDk4NjM0ZDM4ZThmMWIyM2RhOThhNTgyOWQ3N2ZjY2NkMjAwNzljIn0=',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    # Create a folder to store the csv file
    if not os.path.exists('all_drugs'):
        os.makedirs('all_drugs')

    # Open the csv file before entering the loop
    with open('all_drugs/all_drug_names.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for letter in range(ord('a'), ord('z')+1):
            current_url = base_url + chr(letter)
            print(current_url)
            response = requests.get(current_url, headers=headers)
            if response.status_code == 200:
                print(response.status_code)
                soup = BeautifulSoup(response.text, 'lxml')
                root = etree.fromstring(str(soup), etree.HTMLParser())

                # Let's assume the xpath to the element is "/html/body/div/h1"
                xpath = "//div[contains(@class, 'allDrugs')]/div[@id='desktop-all-drugs-container']//span"
                elements = root.xpath(xpath)

                # Write the element text to the csv file
                for element in elements:
                    writer.writerow([element.text])
            else:
                print(f"Status code: {response.status_code}")


scrape_drug_names()
