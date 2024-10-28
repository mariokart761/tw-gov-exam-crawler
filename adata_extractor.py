import pdfplumber
import re


with pdfplumber.open('101年_三等考試_一般民政_法學知識與英文（包括中華民國憲法、法學緒論、英文）_答案.pdf') as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
        
print(text)

# 提取題號和答案
pattern = re.compile(r'題號\s*(\d+(?:\s*\d+)*)\s*答案\s*([A-Z\s]+)')
matches = pattern.findall(text)

# 儲存結果的列表
result = []

# 處理每一題
for match in matches:
    question_numbers = match[0].split()
    answers = match[1].split()
    for q_num, answer in zip(question_numbers, answers):
        result.append({"題號": int(q_num), "答案": answer})

# 打印結果
print(result)