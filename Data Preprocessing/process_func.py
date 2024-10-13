import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm

# STT: 1 
# Loại bỏ các dòng có giá trị null hoặc rỗng
def clear_null(df):
    df = df.dropna(how='any')  # Loại bỏ các dòng có giá trị null
    df = df.replace(r'^\s*$', pd.NA, regex=True).dropna()  # Loại bỏ dòng rỗng hoặc chỉ chứa khoảng trắng
    return df

# STT: 2
# Loại bỏ các giá trị trùng lặp
def clear_duplicate(df):
    return df.drop_duplicates()

# STT: 3
# Loại bỏ các thông tin gây nhiễu: link, url, các ký tự kéo dài, dấu câu quá nhiều
def clear_noise(df):
    # Loại bỏ link, URL
    df = df.applymap(lambda x: re.sub(r'http\S+|www.\S+', '...', str(x)))
    # Loại bỏ các ký tự kéo dài như '.....', '-----', '!!!', '???', '\n\n\n'
    df = df.applymap(lambda x: re.sub(r'[\.\-]{5,}|[\?\!]{2,}|\n{2,}', '', str(x)))
    return df

# STT: 4
# Loại bỏ các thông tin vi phạm chính sách: email, số điện thoại, tên tổ chức
def clear_sensitive_info(df, organizations):
    # Loại bỏ email
    df = df.applymap(lambda x: re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', str(x)))
    # Loại bỏ số điện thoại (chuỗi chứa 10 chữ số trở lên)
    df = df.applymap(lambda x: re.sub(r'\b\d{10,}\b', ' ', str(x)))
    
    # Tạo một biểu thức regex từ danh sách các tổ chức
    org_pattern = r'(?i)\b(' + '|'.join(map(re.escape, organizations)) + r')\b'
    # Loại bỏ tên tổ chức từ danh sách truyền vào và thay thế bằng "Bác sĩ AI"
    df = df.applymap(lambda x: re.sub(org_pattern, ' ', str(x)))
    return df

# STT: 5
# Xóa ký tự trắng kéo dài liên tục
def clear_spaces(df):
    # Loại bỏ các khoảng trắng dài (nhiều hơn 1 khoảng trắng liên tục)
    df = df.applymap(lambda x: re.sub(r'\s{2,}', ' ', str(x)))
    return df

# STT: 6
# Xử lý hai cột question và answer
def simple_qa_handle(df, question_col, answer_col, target_col_name):
    df[target_col_name] = '[INS]Bạn là bác sĩ AI tư vấn trả lời câu hỏi cho người dùng [/INS]\nNgười dùng: ' + df[question_col] + '\nBác sĩ AI: [S]' + df[answer_col] + '[/S]'
    return df[[target_col_name]]

# STT: 7
# Xử lý hội thoại dài
def multi_qa_handle(df, qa_col, target_col_name):
    def transform_qa2qas(qa):
        result = []
        current_sentence = "[INS]Bạn là bác sĩ AI tư vấn trả lời câu hỏi cho người dùng [/INS]\n"
        a_index, b_index = qa.find("Người dùng: "), qa.find("Bác sĩ AI: ")
        while a_index != -1 or b_index != -1:
            if a_index < b_index and a_index != -1:
                current_sentence = current_sentence + qa[a_index:b_index].strip() + "\n"
                qa = qa[b_index:]
            else:
                if a_index == -1:
                    result.append(current_sentence + qa[b_index:b_index+11] + "[S]" + qa[b_index+11:].strip() + "[/S]")
                    break
                else:
                    if b_index == -1:
                        break
                    result.append(current_sentence + qa[b_index:b_index+11] + "[S]" + qa[b_index+11: a_index].strip() + "[/S]")
                    current_sentence = current_sentence + qa[b_index:a_index].strip() + "\n"
                    qa = qa[a_index:]
            a_index, b_index = qa.find("Người dùng: "), qa.find("Bác sĩ AI: ")

        return result
    qa_lst = df[qa_col].to_list()
    total = []
    for qa in qa_lst:
        total = total + transform_qa2qas(qa)
    return pd.DataFrame({
        target_col_name: total
    })


# Pretrain data Pipeline
def pretrain_pipeline(configs, target_col_name="text", test_size=0.1, random_state=42, train_path="pretrain_data.csv", test_path="pretrain_test.csv"):
    df_list = []
    for config_name in configs:
        config = configs[config_name]
        if config["format"] == "csv":
            df = pd.read_csv(config["path"])
        if config["format"] == "parquet":
            df = pd.read_parquet(config["path"])
        df = df[[config["text_col"]]]
        df = df.rename(columns={config["text_col"]: target_col_name})
        for process_step in tqdm(config["process_list"], desc=f"Processing Queue {config_name}: "):
            if process_step == 1: df = clear_null(df[[target_col_name]])
            if process_step == 2: df = clear_duplicate(df[[target_col_name]])
            if process_step == 3: df = clear_noise(df[[target_col_name]])
            if process_step == 4: df = clear_sensitive_info(df[[target_col_name]], config["organizations"])
            if process_step == 5: df = clear_spaces(df[[target_col_name]])
        df_list.append(df)
    final_df = clear_duplicate(clear_null(pd.concat(df_list, ignore_index=True)))
    train_df, test_df = train_test_split(final_df, test_size=test_size, random_state=random_state)

    # Save
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print("Data train saved to:", train_path)
    print("Data test saved to:", test_path)

    # Return for analyse
    return train_df, test_df


# Finetune data pipeline
def finetune_pipeline(configs, target_col_name="text", test_size=0.1, random_state=42, train_path="finetune_data.csv", test_path="finetune_test.csv"):
    df_list = []
    for config_name in configs:
        config = configs[config_name]
        df = pd.read_csv(config["path"])
        for process_step in tqdm(config["process_list"], desc=f"Processing Queue {config_name}: "):
            if process_step == 1: df = clear_null(df[[target_col_name]])
            if process_step == 2: df = clear_duplicate(df[[target_col_name]])
            if process_step == 3: df = clear_noise(df[[target_col_name]])
            if process_step == 4: df = clear_sensitive_info(df[[target_col_name]], config["organizations"])
            if process_step == 5: df = clear_spaces(df[[target_col_name]])
            if process_step == 6: df = simple_qa_handle(df, config["question_col"], config["answer_col"], target_col_name)
            if process_step == 7: df = multi_qa_handle(df, config["qa_col"], target_col_name)
        df_list.append(df)
        
    final_df = clear_duplicate(clear_null(pd.concat(df_list, ignore_index=True)))
    train_df, test_df = train_test_split(final_df, test_size=test_size, random_state=random_state)
    
    # Save
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print("Data train saved to:", train_path)
    print("Data test saved to:", test_path)

    # Return for analyse
    return train_df, test_df
        
