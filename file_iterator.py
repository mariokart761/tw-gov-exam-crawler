import os
from tqdm import tqdm
import json
from edata_extractor import PDFQuestionParser
from adata_extractor import PDFAnswerExtractor

def list_directories(folder_path):
    try:
        # 列出資料夾中的所有項目
        all_items = os.listdir(folder_path)
        # 過濾出資料夾
        directories = [item for item in all_items if os.path.isdir(os.path.join(folder_path, item))]
        return directories
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []

def classify_files(folder_path):
    try:
        # 列出資料夾中的所有檔案
        all_items = os.listdir(folder_path)
        # 檔案分類字典
        classified_files = {
            '試題': [],
            '答案': [],
            '更正答案': []
        }

        for item in all_items:
            if os.path.isfile(os.path.join(folder_path, item)):
                # 分割檔名，獲取副檔名前的字串
                parts = item.rsplit('_', 1)
                if len(parts) > 1:
                    file_type = parts[-1].replace('.pdf', '')  # 去除副檔名
                    if file_type in classified_files:
                        classified_files[file_type].append(item)

        return classified_files
    except Exception as e:
        print(f"發生錯誤: {e}")
        return {}    
if __name__ == "__main__":
    exam_years = [
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112
        ]
    for exam_year in exam_years:
        考試年份 = exam_year
        lv1_folder = f'./考選部考古題pdf/{考試年份}年考選部考古題'  #考試年份
        lv2_folder = list_directories(lv1_folder)  #考試名稱:list
        data=[]
        for 考試名稱 in tqdm(lv2_folder, desc='Parsing PDF content', unit="its"):
            lv3_folder = list_directories(f"{lv1_folder}/{考試名稱}") #考試科目:list
            for 考試科目 in lv3_folder:
                lv3_path = f'{lv1_folder}/{考試名稱}/{考試科目}'
                pdf_file = classify_files(lv3_path)
                
                試題_path = f'{lv3_path}/{pdf_file["試題"][0]}'
                答案_path = f'{lv3_path}/{pdf_file["答案"][0]}'
                # 檢查是否有更正答案，有則使用"更正答案"，反之則用"答案"
                更正答案_path = [""]
                if pdf_file["更正答案"]!=[]:
                    更正答案_path = f'{lv3_path}/{pdf_file["更正答案"][0]}'
                    ans = PDFAnswerExtractor(更正答案_path).get_results()
                else: ans = PDFAnswerExtractor(答案_path).get_results()
                    
                q_parser = PDFQuestionParser(試題_path)
                q_parser.integrate_answers(ans)
                考卷內容 = q_parser.get_questions()
                
                考試資料 = {
                    "考試年份":考試年份,
                    "考試名稱":考試名稱,
                    "考試科目":考試科目,
                    "考卷內容":考卷內容
                }
                
                data.append(考試資料)

        # 存為json
        with open(f'./考選部考古題json/{考試年份}_考古題.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4) 
