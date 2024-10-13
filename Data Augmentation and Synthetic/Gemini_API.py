import json
import asyncio
import google.generativeai as genai

# Config API function
def config_API(API_KEY):
    genai.configure(api_key=API_KEY)
    
# Request function
def request(API_KEY, model_name="gemini-1.0-pro", prompt=None):
    try:
        if prompt is not None:
            config_API(API_KEY)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        else:
            print("Prompt must be NOT None!")
            return None
    except:
        print("\nSomething went wrong! Try again!")
        return None
    
# Get available models and API
def get_available_models_from_file(json_file_path):
    # Load dữ liệu từ file JSON
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    available_models = []
    
    # Duyệt qua từng user trong JSON
    for user, api_keys in data.items():
        # Duyệt qua từng API_KEY trong user
        for api_key, api_data in api_keys.items():
            # Duyệt qua từng model trong API_KEY
            for model_name, model_data in api_data.items():
                # Kiểm tra nếu đó là một model và có available = 1
                if isinstance(model_data, dict) and model_data.get("available") == 1:
                    available_models.append((api_keys[api_key]["API"], model_name))
    
    return available_models

# Set models to unavailable status
def set_unavailable_models(API, model_name, json_file_path):
    # Load dữ liệu từ file JSON
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    for user, api_keys in data.items():
        for api_key in api_keys:
            if api_keys[api_key]["API"] == API:
                api_keys[api_key][model_name]["available"] = 0
                break
            
    with open(json_file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    