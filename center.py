import os
import shutil
from PIL import Image
import numpy as np

def contains_chinese(text):
    """检查字符串是否包含中文字符（不包括标点）"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 基本汉字Unicode范围
            return True
    return False

def find_non_white_region(img, threshold=240):
    """检测图像非空白区域的垂直范围"""
    gray = img.convert('L')
    arr = np.array(gray)
    height, width = arr.shape
    
    # 检测每行是否包含非白像素
    non_white_rows = []
    for y in range(height):
        row = arr[y, :]
        if np.any(row < threshold):  # 存在深于阈值的像素
            non_white_rows.append(y)
    
    if not non_white_rows:
        return 0, height - 1  # 全白图像返回整个高度
    
    top = min(non_white_rows)
    bottom = max(non_white_rows)
    return top, bottom

def center_image_vertically(img, top, bottom):
    """将指定区域居中放置在白色背景上"""
    content_height = bottom - top + 1
    total_height = img.height
    new_img = Image.new('RGB', (img.width, total_height), (255, 255, 255))
    
    # 计算居中位置
    y_offset = max(0, (total_height - content_height) // 2)
    
    # 裁剪非空白区域并粘贴到新位置
    content_block = img.crop((0, top, img.width, bottom + 1))
    new_img.paste(content_block, (0, y_offset))
    return new_img

def process_images(input_dir, output_dir):
    """处理输入目录中的所有PNG文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith('.png'):
            continue
            
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # 非中文文件直接复制
        if not contains_chinese(filename):
            shutil.copy2(input_path, output_path)
            print(f"Copied: {filename}")
            continue
            
        # 处理中文文件
        try:
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 查找非空白区域
                top, bottom = find_non_white_region(img)
                
                # 居中处理并保存
                centered = center_image_vertically(img, top, bottom)
                centered.save(output_path)
                print(f"Processed: {filename} (content height: {bottom-top+1}px)")
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_directory = "handwriting_chars"  # 修改为你的输入目录
    output_directory = "output_chars"
    process_images(input_directory, output_directory)