import PyPDF2
import json
import pandas as pd
import datetime

# PDF to TXT Files function 
def pdf2text(pdf_filepath, index_config_path):
    # Dictionary chứa tên bệnh và số trang bắt đầu
    with open(index_config_path, 'r', encoding="utf-8") as f:
        disease_dict = json.load(f)

    result = []
    # Lấy danh sách các bệnh sắp xếp theo số trang
    diseases_sorted = sorted(disease_dict.items(), key=lambda x: x[1])
            
    with open(pdf_filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_id, page in enumerate(reader.pages):
            # Duyệt qua từng bệnh để tìm khoảng trang
            title = ""
            for i in range(len(diseases_sorted)):
                disease, start_page = diseases_sorted[i]
                if i + 1 < len(diseases_sorted):
                    next_start_page = diseases_sorted[i + 1][1]
                    if start_page <= page_id + 1< next_start_page:
                        title = disease
                        break
                else:
                    if start_page <= page_id + 1:
                        title = disease
                        break
            result.append((title, page.extract_text()))
    return result
                
# Data Dict to CSV files
def data_dict2csv(data_dict, output_path):
    df = pd.DataFrame(data_dict)
    df.to_csv(output_path, index=False)

# Load configuration function
def load_config(config_path):
    with open(config_path, 'r', encoding="utf-8") as f:
        return json.load(f)
    
# Get str time now function
def get_time():
    return datetime.now().strftime('%H:%M %d/%m/%Y')

# str to time
def str2time(s):
    return datetime.strptime(s, '%H:%M %d/%m/%Y')
    