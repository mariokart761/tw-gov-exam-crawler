import pdfplumber
import re
from typing import List, Dict, Optional

class PDFQuestionParser:
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
    
    def __init__(self, filename: str):
        self.filename = filename
        self.questions: List[Dict[str, Optional[str]]] = []
        self.group_ranges: List[Dict[str, int]] = []
        self.conversion_dict = {
            '': ' [A]',
            '': ' [B]',
            '': ' [C]',
            '': ' [D]'
        }
        self.qgroup_patterns = [
            re.compile(r'第(\d+)題至第(\d+)題為題組。?(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL), # 第n題至第m題為題組
            re.compile(r'請依下文回答第(\d+)～(\d+)題。?(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL), # 請依下文回答第39～41題
            re.compile(r'請依下文回答第(\d+)題至第(\d+)題。?(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL), # 請依下文回答第42題至第45題
            re.compile(r'依此回答下列第(\d+)題至第(\d+)題。?(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL), # 依此回答下列第37題至第38題
            re.compile(r'請回答第(\d+)題至第(\d+)題：?(.*?)(?=\[\d+\]\s|\Z)', re.DOTALL), # 請回答第42題至第45題：
        ]
        self.qgroup_title_patterns = [
            re.compile(r'第\d+題至第\d+題為題組.*'),
            re.compile(r'請依下文回答第\d+～\d+題.*'),
            re.compile(r'請依下文回答第\d+題至第\d+題.*'),
            re.compile(r'依此回答下列第\d+題至第\d+題.*'),
            re.compile(r'請回答第\d+題至第\d+題.*'),
        ]
        self.parse_pdf()

    def parse_pdf(self) -> None:
        with pdfplumber.open(self.filename) as pdf:
            text = ''.join(page.extract_text() for page in pdf.pages)

        # 逐行處理提取的文本
        lines = text.split('\n')
        converted_lines = []
        question_counter = 1

        for line in lines:
            for char, letter in self.conversion_dict.items():
                line = line.replace(char, letter)
            
            if line and line.split(' ', 1)[0].isdigit() and ("." not in line.split(' ', 1)[0]):
                if int(line.split(' ', 1)[0]) == question_counter:
                    question_counter += 1
                    parts = line.split(' ', 1)
                    if len(parts) > 1:
                        line = f' [{parts[0]}] {parts[1]}'
            converted_lines.append(line)

        text_content = "".join(converted_lines)
        fixed_content = self.clean_text_content(text_content)
        self.extract_groups(fixed_content)
        self.extract_questions(fixed_content)

    def clean_text_content(self, text_content: str) -> str:
        """
        解決出現以下字串的情況，各字元間允許空格
            代號：50140｜51140頁次：4－2
            代號：30160-30660、30860頁次：4－3
            代號：50130-5063050830-5123051430-51530頁次：4－2
            代 號：50140｜51140頁次：4－2
            代號：50130｜51130頁次：4－2
            代號：2501頁次：4－2"
        """
        sub_contents = [
            r'代號：\d+頁次：\d+－\d+',
            r'代號：\d+-\d+、\d+頁次：\d+－\d',
            r'代號：\d+-\d+-\d+-\d+頁次：\d+－\d',
            r'代\s*號\s*：\s*\d+\s*｜\s*\d+\s*頁\s*次\s*：\s*\d+\s*－\s*\d+',
        ]
        for sub_content in sub_contents:
            fixed_content = re.sub(sub_content, '', text_content)
        return fixed_content

    def extract_groups(self, text_content: str) -> None:
        for pattern in self.qgroup_patterns:
            group_matches = pattern.findall(text_content)
            for match in group_matches:
                self.group_ranges.append({
                    "起始題": int(match[0]),
                    "結束題": int(match[1]),
                    "描述": match[2].strip()
                })

    def extract_questions(self, text_content: str) -> None:
        pattern = re.compile(
            r"\[(\d+)\]\s(.*?)\[(A)\](.*?)\[(B)\](.*?)\[(C)\](.*?)\[(D)\](.*?)(?=\[\d+\]\s|\Z)",
            re.DOTALL
        )
        matches = pattern.findall(text_content)

        for match in matches:
            question = {
                "題號": int(match[0]),
                "題目": match[1].strip(),
                "A": match[3].strip(),
                "B": match[5].strip(),
                "C": match[7].strip(),
                "D": match[9].strip(),
                "題組": next(
                    (group for group in self.group_ranges if group["起始題"] <= int(match[0]) <= group["結束題"]),
                    None
                )
            }
            for key in ['A', 'B', 'C', 'D']:
                for qgroup_title in self.qgroup_title_patterns:
                    question[key] = re.sub(qgroup_title, '', question[key]).strip()

            self.mark_flag(question)
            self.questions.append(question)

    def mark_flag(self, question: Dict[str, str]) -> None:
        # （15 分）這類keyword用來篩選掉申論題
        # "依此回答下"、"回答第"、"依下文" 用來篩選可能沒篩乾淨的題組
        keywords = [
            "頁次", "題組", "代號", "依此回答下", "回答第", "依下文",
            "（50分）", "（25 分）", "（15 分）"
        ]
        question['flag'] = "讚"  # 默認為讚
        if any(keyword in question['題目'] or keyword in question[key] for key in ['A', 'B', 'C', 'D'] for keyword in keywords):
            question['flag'] = "蛋雕"

    def integrate_answers(self, answers: List[Dict[str, str]]) -> None:
        answer_dict = {ans['題號']: ans['答案'] for ans in answers}
        for question in self.questions:
            question['答案'] = answer_dict.get(question['題號'], None)
            # 更正答案中，答案可能會有"#"字元，遇到則蛋雕
            if question['答案'] == "#":
                question['flag'] = "蛋雕 (有不明確的更正答案)"

    def get_questions(self) -> List[Dict[str, Optional[str]]]:
        return self.questions

# if __name__ == "__main__":
#     from adata_extractor import PDFAnswerExtractor
#     q_parser = PDFQuestionParser('101年_三等考試_一般民政_法學知識與英文（包括中華民國憲法、法學緒論、英文）_試題.pdf')
#     ans = PDFAnswerExtractor('101年_三等考試_一般民政_法學知識與英文（包括中華民國憲法、法學緒論、英文）_答案.pdf').get_results()
#     q_parser.integrate_answers(ans)
#     q_data = q_parser.get_questions()
#     for q in q_data:
#         print(q)