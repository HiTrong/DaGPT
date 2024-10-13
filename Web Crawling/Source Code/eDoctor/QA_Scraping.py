# import library
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
import queue
import time

# URL & PATH
url = "https://edoctor.io/hoi-dap"
url_template = "https://edoctor.io{}"
output_path = "medical_qa_scraping.csv"
specialty_output_path = "da_lieu_qa_scraping.csv"
specialty = "cau-hoi-bac-si-chuyen-khoa-da-lieu"

# Data
data_dict = {
    "specialty": [],
    "links": [],
    "question": [],
    "answer": []
}

specialty_data_dict = {
    "specialty": [],
    "links": [],
    "question": [],
    "answer": []
}

# Save csv function
def save_csv(data:dict, path:str):
    df = pd.DataFrame(data)
    df.to_csv(path)

# Multiwork Function: giúp thực hiện nhiều function, công việc cùng lúc
def multiwork(func, inputs:list, number_of_workers: int):
    with ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        results = list(executor.map(func, inputs))
    return results

# Get html with selenium Function: Hàm này lấy source html của một trang web dùng được cho các web sử dụng javascript để load data lên
def get_html_with_selenium(url):
    while True:
        try:
            # Khởi động trình duyệt Chrome với WebDriverManager
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.set_page_load_timeout(10)
            # Điều hướng đến trang web
            driver.get(url)

            # Lấy mã HTML của trang
            html_source = driver.page_source
            driver.quit()
            return html_source
        except:
            print(f"Can't get connection to {url}! Try again in 3 seconds.")
            time.sleep(3)

def get_scrolled_html_with_selenium(url):
    while True:
        try:
            # Khởi động trình duyệt Chrome với WebDriverManager
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.set_page_load_timeout(10)
            # Điều hướng đến trang web
            driver.get(url)
            
            # Lấy chiều cao ban đầu của trang
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                try:
                    # Cuộn xuống cuối trang
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Đợi một thời gian để nội dung mới được tải (thời gian này có thể thay đổi tuỳ theo tốc độ tải của trang)
                    time.sleep(2)
                    
                    # Lấy chiều cao mới sau khi cuộn
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    
                    # Kiểm tra nếu không có nội dung mới tải nữa thì dừng cuộn
                    if new_height == last_height:
                        break
                    
                    # Cập nhật chiều cao mới để tiếp tục cuộn
                    last_height = new_height
                    
                except:
                    print(f"Can't get connection to {url}! Try again in 3 seconds.")
                    time.sleep(3)

            # Lấy mã HTML của trang
            html_source = driver.page_source
            driver.quit()
            return html_source
        except:
            print(f"Can't get connection to {url}! Try again in 3 seconds.")
            time.sleep(3)

# Get QA content Function: hàm này dùng để lấy thông tin hỏi đáp giữa người dùng và bác sĩ, lấy cả các url liên quan đến câu hỏi
def get_QA(url):
    html_content = get_html_with_selenium(url)
    
    # Lấy QA
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.select('.AnswerDetail_content__ZNHPp')
    try:
        question = str(elements[0].text)
        answer = str(elements[1].text)
    except:
        question = None
        answer = None
    
    # Lấy url
    related_url = []
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href.startswith("/hoi-dap/"):
            related_url.append(href)
            
    # Return
    return question, answer, related_url
    
# Main
specialty_mapping = {
    "cau-hoi-bac-si-chuyen-khoa-dinh-duong": "Khoa dinh dưỡng",
    "cau-hoi-bac-si-chuyen-khoa-noi-khoa": "Khoa nội",
    "cau-hoi-bac-si-chuyen-khoa-da-lieu": "Khoa da liễu",
    "cau-hoi-bac-si-chuyen-khoa-than-kinh-and-co-xuong-khop": "Khoa thần kinh và cơ xương khớp",
    "cau-hoi-bac-si-chuyen-khoa-noi-khoa-noi-tiet": "Khoa nội tiết",
    "cau-hoi-bac-si-chuyen-khoa-san-phu-khoa": "Khoa sản phụ",
    "cau-hoi-bac-si-chuyen-khoa-nhi-khoa": "Khoa nhi",
    "cau-hoi-bac-si-chuyen-khoa-tai-mui-hong": "Khoa tai mũi họng",
    "cau-hoi-bac-si-chuyen-khoa-rang-ham-mat": "Khoa răng hàm mặt",
    "cau-hoi-bac-si-chuyen-khoa-nam-khoa": "Khoa nam",
    "cau-hoi-bac-si-chuyen-khoa-phuc-hoi-chuc-nang-than-kinh-and-co-xuong-khop": "Khoa phục hồi chức năng, thần kinh và cơ xương khớp",
    "cau-hoi-bac-si-chuyen-khoa-mat": "Khoa mắt",
    "cau-hoi-bac-si-chuyen-khoa-tieu-hoa": "Khoa tiêu hóa",
    "cau-hoi-bac-si-chuyen-khoa-noi-tiet": "Khoa nội tiết",
    "cau-hoi-bac-si-chuyen-khoa-ho-hap": "Khoa hô hấp",
    "cau-hoi-bac-si-chuyen-khoa-tam-ly-and-tam-than": "Khoa tâm lý và tâm thần",
    "cau-hoi-bac-si-chuyen-khoa-noi-khoa-tim-mach": "Khoa tim mạch",
    "cau-hoi-bac-si-chuyen-khoa-ngoai-khoa-noi-khoa": "Khoa ngoại - nội",
    "cau-hoi-bac-si-chuyen-khoa-tim-mach": "Khoa tim mạch"
}
all_url = []
queue_url = queue.Queue()
def main(check_point=5, batch_size=20):
    # Mở trang web chính và scroll để load các câu hỏi đáp
    html_content = get_scrolled_html_with_selenium(url)
    # Lấy href các bài viết thêm vào hàng chờ nếu chưa được xử lý
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href.startswith("/hoi-dap/") and url_template.format(href) not in all_url:
            all_url.append(url_template.format(href))
            queue_url.put(url_template.format(href))
            
    # Lấy QA từ các url trong hàng chờ
    process_urls = []
    while queue_url.empty() == False:
        batch_url = []
        while len(batch_url) < batch_size and queue_url.empty() == False:
            batch_url.append(queue_url.get())
        process_urls.append(batch_url)

        if len(process_urls) == check_point or queue_url.empty():
            for process_url in tqdm(process_urls, desc=f"Crawling urls with batch_size={batch_size}: "):
                # Xử lý process_url
                results =  multiwork(get_QA, process_url, number_of_workers=5)
                for i, result in tqdm(enumerate(results), desc=f"Inserting {len(results)} QA: "):
                    question, answer, related_url = result
                    
                    # Thêm vào data_dict
                    data_dict["question"].append(question)
                    data_dict["answer"].append(answer)
                    data_dict["links"].append(process_url[i])
                    spe = "Chủ đề nổi bật"
                    for key in specialty_mapping:
                        if key in process_url[i]:
                            spe = specialty_mapping[key]
                            
                            # Specialty
                            if key == specialty:
                                specialty_data_dict["question"].append(question)
                                specialty_data_dict["answer"].append(answer)
                                specialty_data_dict["links"].append(process_url[i])
                                specialty_data_dict["specialty"].append(spe)
                            
                            break
                    data_dict["specialty"].append(spe)
                    save_csv(data_dict, output_path)
                    save_csv(specialty_data_dict, specialty_output_path)
                    
                    # Xử lý related_url
                    for href in related_url:
                        if url_template.format(href) not in all_url:
                            all_url.append(url_template.format(href))
                            queue_url.put(url_template.format(href))
                            
            # Reset
            process_urls = []
            
main()