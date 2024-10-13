# Import Library
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Output
data_dict = {
    "headline": [],
    "links": [],
    "content": []
}
output_path = "medical_article_scraping.csv"

# Link search
link_search = "https://edoctor.io/bai-viet/tim-kiem?s={}&page={}"
link_homepage = "https://edoctor.io{}"

# Request and Analyze Function
def request_and_analyze(url):
    while True:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                return html_content
            else:
                print(f"Failed to retrieve content. Status code: {response.status_code}")
                print("Try again in 3 seconds.")
                time.sleep(3)
        except:
            print(f"\nFailed to connect to server")
            print("Try again in 10 seconds.")
            time.sleep(10)


# Load keyword
keywords = []
try:
    with open("search_keyword.txt","r",encoding="utf-8") as f:
        for keyword in f:
            keywords.append(keyword.replace("\n","").replace(" ","+"))     
    print(f"Đã load {len(keywords)} từ khóa!")
except:
    raise Exception("Không load được từ khóa!")

# Searching
links_found = []
for keyword in tqdm(keywords, desc=f"SEARCHING PROGRESS: "):
    print()
    total = 0
    page = 1
    while True:
        url = link_search.format(keyword, page)
        
        # Gửi yêu cầu HTTP để lấy nội dung HTML
        html_content = request_and_analyze(url)
                
        # Lấy link các bài viết
        link_add = []
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href is not None:
                if "/bai-viet/" in href and href not in links_found:
                    link_add.append(href)
        if len(link_add) > 0:
            links_found = links_found + link_add
            total += len(link_add)
            # Start scrapping links
            for link in tqdm(link_add, desc=f"Keyword {keyword} - Page {page} - {len(link_add)} links: "):
                url = link_homepage.format(link)
                html_content = request_and_analyze(url)
                soup = BeautifulSoup(html_content, 'html.parser')
                contents = soup.find_all('p')
                headlines = soup.find_all('h1')
                for content in contents:
                    # Bỏ nguồn và bỏ ----
                    if "Nguồn: " in content.text or "-----" in content.text:
                        break
                    
                    if headlines is not None:
                        data_dict["headline"].append(headlines[0].text)
                    else:
                        data_dict["headline"].append(keyword.replace("+"," "))
                    data_dict["links"].append(url)
                    data_dict["content"].append(content.text)
                
            link_add = []
            page += 1
        else:
            break
    # Save data
    df = pd.DataFrame(data_dict)
    df.to_csv(output_path)
    print("Data saved to:",output_path)
    
print(f"Scrapping {total} articles with {len(data_dict['content'])} rows.")



    
    
