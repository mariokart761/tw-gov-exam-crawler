import pdfplumber
import re
"""
將題目與選項整理成list[dict]形式，且解決
    題號受到題目中有數字而被汙染
    換頁時會有頁次、代號字樣
    出現題組時，選項內容受到汙染
    等問題
    
並記額外紀錄
    每一題的flag資訊，若該題的題目或選項中帶有指定字串，則將該題的flag標記為"蛋雕"，否則標記為"讚"
    若為題組，則該題資料中會有"題組題的起始題、結束題、描述"，否則為None
"""

# 定義字符與字母的對應關係
conversion_dict = {
    '': ' [A]',
    '': ' [B]',
    '': ' [C]',
    '': ' [D]'
}

# 打開PDF文件
with pdfplumber.open('101年_三等考試_一般民政_法學知識與英文（包括中華民國憲法、法學緒論、英文）_試題.pdf') as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text()

# 逐行處理提取的文本
lines = text.split('\n')
converted_lines = []
題號counter = 1

for line in lines:
    for char, letter in conversion_dict.items():
        line = line.replace(char, letter)
    
    # 依題序檢查re檢測到的數字是否為題號，達成條件則將該'數字'轉為'[數字]'格式
    if line and line[0].isdigit() and ("." not in line.split(' ', 1)[0]):
        # if ("." not in line.split(' ', 1)[0]):
        if int(line.split(' ', 1)[0]) == 題號counter:
            題號counter += 1
            parts = line.split(' ', 1)
            if len(parts) > 1:
                line = f' [{parts[0]}] {parts[1]}'
        
    converted_lines.append(line)

# 將轉換後的結果合成為單一字串
text_content = "".join(converted_lines)

# 使用正則表達式剔除不需要的內容
text_content = re.sub(r'代號：\d+頁次：\d+－\d+', '', text_content)

# 提取題組範圍和描述
group_ranges = []
group_pattern = re.compile(r'第(\d+)題至第(\d+)題為題組(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL)
group_matches = group_pattern.findall(text_content)

for match in group_matches:
    group_ranges.append({
        "起始題": int(match[0]),
        "結束題": int(match[1]),
        "描述": match[2].strip()  # 取出題組描述並去掉多餘空格
    })

# 使用正則表達式提取問題及選項
questions = []
pattern = re.compile(r"\[(\d+)\]\s(.*?)\[(A)\](.*?)\[(B)\](.*?)\[(C)\](.*?)\[(D)\](.*?)(?=\[\d+\]\s|\Z)", re.DOTALL)

matches = pattern.findall(text_content)

for match in matches:
    question = {
        "題號": int(match[0]),
        "題目": match[1].strip(),
        "A": match[3].strip(),
        "B": match[5].strip(),
        "C": match[7].strip(),
        "D": match[9].strip(),
        "題組範圍": next((group for group in group_ranges if group["起始題"] <= int(match[0]) <= group["結束題"]), None)
    }
    # 清除不需要的部分
    for key in ['A', 'B', 'C', 'D']:
    # 正則表達式清除題組標記及後續內容
        question[key] = re.sub(r'第\d+題至第\d+題為題組.*', '', question[key]).strip()
        
    questions.append(question)

# 測試用
# questions=[
#     {'題號': 27, '題目': '刑法關於中華民國國防以外秘密之保護，下列敘述何者正確？', 'A': '刑法關於公務員洩漏中華民國國防以外秘密罪，只設處罰公務員之故意洩漏行為', 'B': '刑法關於公務員洩漏中華民國國防以外秘密罪，行為客體以經完成機密核定者為限', 'C': '洩漏中華民國國防以外秘密，行為主體不以公務員為限，非公務員亦有觸犯可能', 'D': '公務員假藉職務上之機會，故意洩漏中華民國國防以外秘密者，加重其刑至二分之一', '題組範圍': None, 'flag': ''},
#     {'題號': 28, '題目': '下列公司中，何者所有權與經營權分離 頁次4-5之程度最高？', 'A': '無限公司', 'B': '兩合公司', 'C': '有限公司', 'D': '股份有限公司', '題組範圍': None, 'flag': ''},
#     {'題號': 29, '題目': '如勞工對雇主實施暴行，則有關下列敘述何者錯誤？', 'A': '雇主得不經預告終止勞動契約', 'B': '發生暴行後，雇主應於三十日內終止勞動契約，否則以後不得以同一事件終止勞動契約', 'C': '如勞 工年資達五年以上，雇主終止勞動契約，仍應給予資遣費', 'D': '雇主終止勞動契約，不須給予資遣費', '題組範圍': None, 'flag': ''}
# ]

# 標記問題
for question in questions:
    if any((keyword in question['題目'])
            or(keyword in question['A'])
            or(keyword in question['B'])
            or(keyword in question['C'])
            or(keyword in question['D'])
           for keyword in ["頁次", "科目", "題組"]):
        question['flag'] = "蛋雕"
    else:
        question['flag'] = "讚"

# # 輸出結果
# print("\n讚 的題目")
# for q in questions:
#     if q['flag'] == "讚": print(q)
# print("\n蛋雕 的題目")
# for q in questions:
#     if q['flag'] == "蛋雕": print(q)

# # 輸出題組範圍和描述
# print("\n題組範圍和描述：")
# for group in group_ranges:
#     print(group)
