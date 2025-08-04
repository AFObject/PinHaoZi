import os
from paddleocr import PaddleOCR
from collections import defaultdict

# 初始化 OCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang='ch'
)

# 设置你的图片文件夹路径
image_folder = "cropjb1"  # TODO：修改为你的图片文件夹路径

# 重名计数器
char_count = defaultdict(int)

# 支持的图片格式
valid_exts = {".png", ".jpg", ".jpeg", ".bmp"}

# 遍历文件夹
for filename in os.listdir(image_folder):
    name, ext = os.path.splitext(filename)
    if ext.lower() not in valid_exts:
        continue

    image_path = os.path.join(image_folder, filename)
    result = ocr.predict(image_path)
    
    # print(result)

    try:
        char = result[0]['rec_texts'][0].strip()
        if not char:
            raise ValueError
    except (IndexError, KeyError, TypeError, ValueError):
        print(f"未能识别：{filename}")
        continue


    # 处理重名
    count = char_count[char]
    new_name = f"{char}.png" if count == 0 else f"{char}-{count}.png"
    char_count[char] += 1

    # 重命名文件
    old_path = os.path.join(image_folder, filename)
    new_path = os.path.join(image_folder, new_name)
    os.rename(old_path, new_path)
    print(f"{filename} → {new_name}")
