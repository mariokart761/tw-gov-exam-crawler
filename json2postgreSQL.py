from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from typing import Optional, List
import json
import configparser

class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int = Field(index=True, alias="考試年份")
    name: str = Field(alias="考試名稱")
    subject: str = Field(alias="考試科目")
    questions: List["Question"] = Relationship(back_populates="exam")

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="exam.id")
    number: int = Field(alias="題號")
    question_text: str = Field(alias="題目")
    option_a: str = Field(alias="A")
    option_b: str = Field(alias="B")
    option_c: str = Field(alias="C")
    option_d: str = Field(alias="D")
    flag: Optional[str]
    answer: str = Field(alias="答案")
    question_group: Optional[str] = Field(alias="題組")

    exam: Optional[Exam] = Relationship(back_populates="questions")

# 建立資料庫連線
config = configparser.ConfigParser()
config.read('config.conf')
# 格式範例 postgresql://username:password@localhost:5432/mydatabase
DATABASE_URL = config['database']['url']
engine = create_engine(DATABASE_URL)

# 建立資料表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def load_json_to_db(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with Session(engine) as session:
        for exam_data in data:
            exam = Exam(
                year=exam_data["考試年份"],
                name=exam_data["考試名稱"],
                subject=exam_data["考試科目"]
            )
            session.add(exam)
            session.commit()  # 確保考試資料插入後，才能建立外鍵連結

            for question_data in exam_data["考卷內容"]:
                question = Question(
                    exam_id=exam.id,
                    number=question_data["題號"],
                    question_text=question_data["題目"],
                    option_a=question_data["A"],
                    option_b=question_data["B"],
                    option_c=question_data["C"],
                    option_d=question_data["D"],
                    flag=question_data.get("flag"),
                    answer=question_data["答案"],
                    question_group=question_data.get("題組")
                )
                session.add(question)

        session.commit()


if __name__ == "__main__":
    # 建立資料庫表
    create_db_and_tables()
    # 載入 JSON 資料
    load_json_to_db("path_to_your_json_file.json")
