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
from concurrent.futures import ThreadPoolExecutor

NUMBER = 20

def synthetic_out_of_scope_qa(model_with_api):
    api, model_name = model_with_api
    prompt_template = process_text.out_of_scope_qa_template(NUMBER)
    try_again = 0
    while True:
        response = request(api, model_name, prompt_template)
        if response is not None:
            break
        if try_again >= 10:
            return [None]
        try_again += 1
    return process_text.extract_response(process_text.clear_response(response))

def pipeline():
    model_with_api_lst = get_available_models_from_file("config_API.json")
    text = []
    for i in tqdm(range(21), desc="Request API Gemini for out_of_scope qa "):
        with ThreadPoolExecutor(max_workers=7) as executor:
            results = list(executor.map(synthetic_out_of_scope_qa, model_with_api_lst))
        for result in results:
            text = text + result
    df = pd.DataFrame({"text": text})
    df.to_csv("out_of_scope_qa2.csv", index=False)
    print("Done!")
    
pipeline()