import PyPDF2
import json
import pandas as pd
import datetime
import time
import queue
import google.generativeai as genai
import process_text
from tqdm.auto import tqdm
from utils import pdf2text, load_config, data_dict2csv
from Gemini_API import request, get_available_models_from_file, set_unavailable_models

# Xử lý hàng chờ model
class ModelQueue:
    def __init__(self, config_path, max_errors=10):
        self.queue = queue.Queue()
        self.max_errors = max_errors
        available_models = get_available_models_from_file(config_path)
        for api, model in available_models:
            self.queue.put((api, model, 0))
            
    def get_model(self):
        if not self.queue.empty():
            return self.queue.get()
        return None
    
    def put_model(self, api, model, number_of_errors):
        if number_of_errors < self.max_errors:
            self.queue.put((api, model, number_of_errors))
        else:
            print(f"Model queue: stopping {model}, {api}")
            set_unavailable_models(api, model, "config_API.json")
        
def request_with_model_queue(prompt, model_queue:ModelQueue):
    api, model_name, number_of_errors = model_queue.get_model()
    try:
        response = request(API_KEY=api, model_name=model_name, prompt=prompt)
        if response == None:
            model_queue.put_model(api, model_name, number_of_errors + 1)
            return None, model_queue
        model_queue.put_model(api, model_name, 0)
        return response, model_queue
    except:
        model_queue.put_model(api, model_name, number_of_errors + 1)
        return None, model_queue

# pipeline 
def pipeline(pdf_filepath="Huong-dan-chan-doan-dieu-tri-Da-lieu.pdf", 
             index_config_path="config_index_pdf.json",
             api_config_path="config_API.json"):
    
    data_augmentation_dict = {
        "title": [],
        "text": []
    }
    
    data_syntheic_dict = {
        "title": [],
        "QA": []
    }
    
    # Step 1: PDF to text (streaming)
    pdf2text_result = pdf2text(pdf_filepath, index_config_path)
    
    # Step 2: Text Editor
    model_queue = ModelQueue(api_config_path, max_errors=10)
    for title, text in tqdm(pdf2text_result, desc="Data Augmentation & Synthetic Data Generation PDF: "):
        editor_prompt = process_text.text_editor_template(text)
        editor_reponse = None
        while editor_reponse is None:
            editor_reponse, model_queue = request_with_model_queue(editor_prompt, model_queue)
        cleaned_editor_response = process_text.extract_response(process_text.clear_response(response=editor_reponse))
        # Step 3: Data Augmentation
        for t in [" ".join(cleaned_editor_response)]:
            for j in tqdm([0,1,2,3,4], desc=f"\nData Augmentation cho bệnh {title}: "):
                augmentation_prompt = process_text.data_augmentation_template(10, f"thông tin về bệnh {title}: {t}")
                augmentation_reponse = None
                while augmentation_reponse is None:
                    augmentation_reponse, model_queue = request_with_model_queue(augmentation_prompt, model_queue)
                cleaned_augmentation_response = process_text.extract_response(process_text.clear_response(augmentation_reponse))
                for a in cleaned_augmentation_response:
                    data_augmentation_dict["title"].append(f"bệnh {title}")
                    data_augmentation_dict["text"].append(a)
        
        # Step 4: Synthetic Data QA Generation
        for t in [" ".join(cleaned_editor_response)]:
            for j in tqdm([0,1,2,3,4,5], desc=f"Synthetic Data Generation cho bệnh {title}: "):
                synthetic_prompt = process_text.synthetic_data_generation_template(10, f"thông tin về bệnh {title}: {t}")
                synthetic_response = None
                while synthetic_response is None:
                    synthetic_response, model_queue = request_with_model_queue(synthetic_prompt, model_queue)
                cleaned_synthetic_response = process_text.extract_response(process_text.clear_response(synthetic_response))
                for a in cleaned_synthetic_response:
                    data_syntheic_dict["title"].append(f"bệnh {title}")
                    data_syntheic_dict["QA"].append(a)
                
        # Step 5: Save to CSV
        print("\n======================================== SAVED! ========================================\n")
        data_dict2csv(data_augmentation_dict, "data_augmentation.csv")
        data_dict2csv(data_syntheic_dict, "data_synthetic.csv")
        
pipeline()
