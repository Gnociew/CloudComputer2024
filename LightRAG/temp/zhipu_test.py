from pdf2image import convert_from_path
import pytesseract

# PDF 文件路径
file_path = 'test.pdf'

# 将 PDF 转换为图像
images = convert_from_path(file_path)

# 初始化文本内容
text_content = ''

# 对每一页进行 OCR
for image in images:
    # 提取中文文本
    text_content += pytesseract.image_to_string(image, lang='chi_sim')

# 打印提取的文本
print(text_content)