import pdfplumber
from soynlp.tokenizer import LTokenizer
from collections import Counter
import random
import re
import unicodedata

def split_tokens(tokens):
    pattern = re.compile(r"(\W|\d+)")
    new_tokens = []
    for token in tokens:
        # 토큰 내의 특수 문자와 숫자를 별도의 토큰으로 분리
        parts = pattern.split(token)
        # 공백이 아닌 토큰만 추가
        parts = [part for part in parts if part.strip()]  # 공백 제거 및 빈 문자열 확인
        if parts:  # 부분이 비어 있지 않은 경우에만 추가
            new_tokens.extend(parts)
    return new_tokens

def remove_suffix(word):
    # 흔히 사용되는 조사나 접미사 리스트
    suffixes = ['을', '를', '이', '가', '은', '는', '의', '에', '으로', '와', '과', '도', '로', '에서', '에게', '까지', '만', '조차', '도', '밖에', '마저', '한테', '랑', '이나', '나', '부터', '처럼', '처럼', '같이', '마냥', '커녕', '보다']
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def generate_questions_korean_soynlp(text, num_questions=3, context_words=100):
    # soynlp 토크나이저 생성
    tokenizer = LTokenizer()
    
    # 텍스트 토크나이징
    tokens = tokenizer.tokenize(text)

    # 토큰 추가 분리
    tokens = split_tokens(tokens)

    # 한국어 불용어 리스트 (예시, 필요에 따라 수정 가능)
    stop_words = [
        '은', '는', '이', '가', '을', '를', '에', '에게', '에서', '와', '과', '도', '만', '처럼', '같이', '로서', '로써', '로', '부터', '까지', '보다', '하고', '등', '등등',
        '그리고', '그러나', '그런데', '하지만', '따라서', '그래서',
        '그', '그녀', '그것', '저', '나', '너', '우리', '여러분', '그들', '제', '내',
        '하다', '되다', '있다', '있는',
        '것', '이런', '저런', '그런', '여기', '저기', '어디', '아무', '무엇', '이것', '저것', '어떤', '다른', '또', '이렇게', '그렇게', '저렇게', '많이', '좀', '조금', '다시', '그러므로', '왜냐하면',
        '통해', '가장', '잘',
        "-", "--", ":", "->", "=", "-", "l", "+", "+", "𝑠", ",", "•", "−", " ", "!", ".", "(", ")", "∶", ">", "𝒊", "[", "∙", "*", "%", "𝑛", "∑", "‘",
        "AI", "융합", "캡스톤", "디자인", "Sogang" ,"수",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "the",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
    ]

    # special_ranges = [
    #     (0x0021, 0x002F),  # Punctuation
    #     (0x003A, 0x0040),  # More punctuation
    #     (0x005B, 0x0060),  # Even more punctuation
    #     (0x007B, 0x007E),  # Guess what? Yes, punctuation
    #     (0x2000, 0x206F),  # General Punctuation
    #     (0x20A0, 0x20CF),  # Currency Symbols
    #     (0x2190, 0x21FF),  # Arrows
    #     (0x2300, 0x23FF),  # Miscellaneous Technical
    #     (0x25A0, 0x25FF),  # Geometric Shapes
    #     (0x2600, 0x26FF),  # Miscellaneous Symbols
    #     (0x2700, 0x27BF),  # Dingbats
    #     (0x2B50, 0x2B59),  # More Miscellaneous Symbols
    #     (0x2900, 0x297F),  # Supplemental Arrows-B
    #     (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
    #     (0x1F600, 0x1F64F),  # Emoticons
    #     (0x1F680, 0x1F6FF),  # Transport and Map Symbols
    # ]
    
    # special_chars = []
    # for start, end in special_ranges:
    #     for code in range(start, end + 1):
    #         if 'CHARACTER' in unicodedata.name(chr(code), ''):
    #             special_chars.append(chr(code))

    #     # special_chars.extend([chr(code) for code in range(start, end + 1) if 'CHARACTER' in unicodedata.name(chr(code), '')])

    # stop_words += special_chars

    # print(stop_words)

    filtered_tokens = []
    for word in tokens:
        if word not in stop_words:
            filtered_tokens.append(word)
        
    
    # 가장 빈번한 단어를 찾습니다.
    word_freq = Counter(filtered_tokens)
    most_common_words = word_freq.most_common(num_questions)
    
    questions = []
    for word, _ in most_common_words:
        # 해당 단어가 나타난 모든 위치를 찾습니다.
        processed_word = remove_suffix(word)
        word_positions = [i for i, w in enumerate(tokens) if remove_suffix(w) == processed_word]

        # 주어진 위치들 중에서 랜덤하게 하나를 선택
        if word_positions:
            pos = random.choice(word_positions)
            start = max(0, pos - context_words)
            end = min(len(tokens), pos + context_words + 1)
            context = tokens[start:end]
            blanked_context = ' '.join(context).replace(processed_word, "______")
            questions.append((f"Fill in the blank: {blanked_context}", processed_word))
    
    return questions

def extract_text_from_pdf(pdf_path):
    # PDF 파일을 열고 내용을 읽습니다.
    pdf_pages=[]
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pdf_pages.append(text)

    return pdf_pages

def main():
    pages = extract_text_from_pdf("ch5.pdf")

    # 문제 생성
    questions = []
    for page in pages:
        questions += generate_questions_korean_soynlp(page)

    # 문제 출력
    for i, (question, answer) in enumerate(questions, 1):
        print(f"Question {i}\n {question}\nAnswer: {answer}\n")



if __name__ == "__main__":
    main()