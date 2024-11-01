import configparser
import json
from sqlmodel import SQLModel, Field, Session, create_engine, text
from typing import List, Optional
from tqdm import tqdm

# 定義數據模型
class ExamQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exam_year: int = Field(alias="考試年份")
    exam_name: str = Field(alias="考試名稱")
    exam_subject: str = Field(alias="考試科目")
    question_number: int = Field(alias="題號")
    question_text: str = Field(alias="題目")
    option_a: str = Field(alias="A")
    option_b: str = Field(alias="B")
    option_c: str = Field(alias="C")
    option_d: str = Field(alias="D")
    question_group: Optional[str] = Field(default=None, alias="題組")  # 將題組設為可選的字符串類型
    flag: str
    answer: str 

# 讀取配置檔案中的資料庫 URL
config = configparser.ConfigParser()
config.read('config.conf')
DATABASE_URL = config['database']['url']
engine = create_engine(DATABASE_URL)

# 建立資料庫表格
SQLModel.metadata.create_all(engine)

# 讀取 JSON 檔案
with open('./考選部考古題json/101_考古題.json', encoding='utf-8') as f:
    data = json.load(f)

# 解析 JSON 資料並插入資料庫
with Session(engine) as db:
    for exam in tqdm(data, desc='Building database', unit="its"):
        exam_year = exam["考試年份"]
        exam_name = exam["考試名稱"]
        exam_subject = exam["考試科目"]
        
        for question in exam["考卷內容"]:
            # 將題組（question_group）轉換為 JSON 字符串格式，若為空則保留 None
            question_group = json.dumps(question["題組"]) if question["題組"] else None
            
            question_data = ExamQuestion(
                exam_year=exam_year,
                exam_name=exam_name,
                exam_subject=exam_subject,
                question_number=question["題號"],
                question_text=question["題目"],
                option_a=question["A"],
                option_b=question["B"],
                option_c=question["C"],
                option_d=question["D"],
                question_group=question_group,
                flag=question["flag"],
                answer=question["答案"]
            )
            db.add(question_data)
    
    db.commit()  # 提交事務以插入資料

# 驗證插入是否成功的範例查詢
# with Session(engine) as db:
#     result = db.exec(text("SELECT * FROM examquestion"))
#     for row in result:
#         print(row)

with Session(engine) as db:
    db_name = db.exec(text("SELECT current_database();")).one()
    print("Connected to database:", db_name)
