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

        # 提取題號和答案
        # 更正答案中，答案可能會有"#"字元
        pattern = re.compile(r'題號\s*(\d+(?:\s*\d+)*)\s*答案\s*([A-Z\s#]+)')
        matches = pattern.findall(text)

        # 儲存結果的列表
        result = []

        # 處理每一題
        for match in matches:
            question_numbers = match[0].split()
            answers = match[1].split()
            for q_num, answer in zip(question_numbers, answers):
                result.append({"題號": int(q_num), "答案": answer.strip()})

        return result

    def get_results(self):
        return self.result

# if __name__ == "__main__":
#     file_path = './101年考選部考古題/三等移民行政特考_移民行政(選試俄文）/國際公法與移民政策（包括移民人權）/101年_三等移民行政特考_移民行政(選試俄文）_國際公法與移民政策（包括移民人權）_更正答案.pdf'
#     extractor = PDFAnswerExtractor(file_path)
#     results = extractor.get_results()
#     print(results)
