from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import requests
import time

"""
爬取考選部網站中，每年帶有 "法"字 科目的檔案，例如："法學大意"
    html內容需先從考選部網站選好條件，直接載下整個html內容後，存至 "./考選部html/<n>年考選部考古題.html"後，
    方可進行解析，並自動下載試題、解答、更正解答。
"""


def href_converter(href_string:str)->str:
    return f'https://wwwq.moex.gov.tw/exam/{href_string.replace("amp;", "")}'
year_list = ["105","104","103","102","101"]
for year in year_list:
    exam_year:str = year
    file_path = f'./考選部html/{exam_year}年考選部考古題.html'

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()


    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='ctl00_holderContent_tblExamQand')
    tds = table.find_all('td')

    result = []
    for td in tqdm(tds, desc="Parsing html", unit="its"):
        label = td.find('label', {"class": "exam-title"})
        if label and '法' in label.text:
            links = td.find_all('a')
            for link in links:
                # 檢查是否包含 <table> 標籤 (否則會因mobile版資料而重複同一筆)
                if link.text in ["答案", "更正答案"] and td.find('table'):
                    result.append(td)
                    break

    # 建構考試資料
    exam_data = []
    for td in tqdm(result, desc="Processing exam data", unit="its"):
        exam_info = {
            "考試名稱": "",
            "科目": "",
            "試題連結": "",
            "答案連結": "",
            "更正答案連結": ""
        }

        # 查找前一個 class="level2" 的 td 標籤
        level2_td = td.find_previous('td', class_='level2')
        if level2_td:
            level2_label = level2_td.find('label')
            if level2_label:
                exam_info["考試名稱"] = level2_label.text.strip()

        # 存入科目
        exam_title_label = td.find('label', {"class": "exam-title"})
        if exam_title_label:
            exam_info["科目"] = exam_title_label.text.strip()

        # 存入試題、答案、更正答案連結
        links = td.find_all('a', class_='exam-question-ans')
        for link in links:
            if link.text == "試題":
                exam_info["試題連結"] = href_converter(link['href'])
            elif link.text == "答案":
                exam_info["答案連結"] = href_converter(link['href'])
            elif link.text == "更正答案":
                exam_info["更正答案連結"] = href_converter(link['href'])

        exam_data.append(exam_info)

    ## 下載考古題
    base_dir = f'./考選部考古題pdf/{exam_year}年考選部考古題'
    os.makedirs(base_dir, exist_ok=True)
    for exam in tqdm(exam_data, desc="Downloading exam data", unit="its"):
        考試名稱 = exam['考試名稱']
        科目 = exam['科目']
        
        exam_folder = os.path.join(base_dir, 考試名稱)
        subject_folder = os.path.join(exam_folder, 科目)
        
        os.makedirs(subject_folder, exist_ok=True)

        # 下載試題 PDF
        試題連結 = exam['試題連結']
        if 試題連結:
            試題檔案名 = f"{exam_year}年_{考試名稱}_{科目}_試題.pdf"
            試題路徑 = os.path.join(subject_folder, 試題檔案名)
            
            if not os.path.exists(試題路徑):
                response = requests.get(試題連結)
                if response.status_code == 200:
                    with open(試題路徑, 'wb') as f:
                        f.write(response.content)
            else:
                print(f"文件 {試題檔案名} 已存在，跳過下載。")

        # 下載答案 PDF
        答案連結 = exam['答案連結']
        if 答案連結:
            答案檔案名 = f"{exam_year}年_{考試名稱}_{科目}_答案.pdf"
            答案路徑 = os.path.join(subject_folder, 答案檔案名)

            if not os.path.exists(答案路徑):
                response = requests.get(答案連結)
                if response.status_code == 200:
                    with open(答案路徑, 'wb') as f:
                        f.write(response.content)
            else:
                print(f"文件 {答案檔案名} 已存在，跳過下載。")

        # 下載更正答案 PDF
        更正答案連結 = exam['更正答案連結']
        if 更正答案連結:
            更正答案檔案名 = f"{exam_year}年_{考試名稱}_{科目}_更正答案.pdf"
            更正答案路徑 = os.path.join(subject_folder, 更正答案檔案名)

            if not os.path.exists(更正答案路徑):
                response = requests.get(更正答案連結)
                if response.status_code == 200:
                    with open(更正答案路徑, 'wb') as f:
                        f.write(response.content)
            else:
                print(f"文件 {更正答案檔案名} 已存在，跳過下載。")
        time.sleep(0.5)
        
    print(f"{exam_year}年考古題所有檔案下載完成。")

