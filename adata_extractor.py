import pdfplumber
import re

class PDFAnswerExtractor:
    def __init__(self, filename):
        self.filename = filename
        self.result = self.extract_answers()

    def extract_answers(self):
        with pdfplumber.open(self.filename) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()

        # 更新提取題號和答案的正則表達式
        pattern = re.compile(r'題號\s*(第?\d+題?(?:\s*第?\d+題?)*)\s*答案\s*([A-Z\s#]*)')
        matches = pattern.findall(text)

        # 儲存結果的列表
        result = []

        # 處理每一題
        for match in matches:
            question_numbers = match[0].split()
            answers = match[1].strip().split() if match[1].strip() else []
            for q_num in question_numbers:
                if answers:
                    answer = answers.pop(0)  # 取出第一個答案
                else:
                    answer = None  # 如果沒有答案
                result.append({"題號": int(re.sub(r'第|題', '', q_num)), "答案": answer})

        return result

    def get_results(self):
        return self.result

# if __name__ == "__main__":
#     file_path = './102年考選部考古題/三等考試_農業行政/法學知識與英文（包括中華民國憲法、法學緒論、英文）/102年_三等考試_農業行政_法學知識與英文（包括中華民國憲法、法學緒論、英文）_更正答案.pdf'
#     extractor = PDFAnswerExtractor(file_path)
#     results = extractor.get_results()
#     print(results)