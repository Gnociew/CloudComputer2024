from docx import Document

def convert_word_to_txt(word_file, txt_file):
    # 打开 Word 文档
    doc = Document(word_file)
    
    # 创建一个空字符串来存储文本内容
    full_text = []
    
    # 遍历文档中的每个段落，并将其添加到 full_text 列表中
    for para in doc.paragraphs:
        full_text.append(para.text)
    
    # 将段落文本连接成一个字符串，并写入到 .txt 文件中
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_text))

# 使用示例
word_file = '普通高中教科书生物学必修1-分子与细胞.docx'  # 输入的 Word 文件路径
txt_file = '生物必修一.txt'     # 输出的文本文件路径
convert_word_to_txt(word_file, txt_file)
