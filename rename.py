import os
import re
import shutil
from PIL import Image

def custom_sort_key(filename):
    """
    一个自定义排序键，用于从文件名中提取 row-X 和 part-Y 的数字值。
    """
    match = re.search(r'row-(\d+)_part-(\d+)', filename)
    if match:
        row_num = int(match.group(1))
        part_num = int(match.group(2))
        return (row_num, part_num)
    return (float('inf'), float('inf'))

def is_blank_image(image_path, threshold=5):
    """
    检查图片是否为空白。
    """
    try:
        with Image.open(image_path) as img:
            gray_img = img.convert('L')
            pixels = list(gray_img.getdata())
            avg_pixel_value = sum(pixels) / len(pixels)

            if avg_pixel_value < threshold or avg_pixel_value > 255 - threshold:
                return True
            return False
    except Exception as e:
        print(f"处理图片 {image_path} 时出错: {e}")
        return False

def process_and_copy_images(folder_path, names_text):
    # 创建 output 文件夹
    output_folder = os.path.join(folder_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    print(f"已确保输出文件夹 {output_folder} 存在。")

    # 获取文件夹中所有图片文件
    all_image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # 使用自定义排序键进行排序
    all_image_files.sort(key=custom_sort_key)
    
    # 存储非空白的图片路径
    images_to_copy = []

    # 第一步：筛选出非空白图片
    print("\n正在筛选和删除空白图片...")
    for image_name in all_image_files:
        image_path = os.path.join(folder_path, image_name)
        if not is_blank_image(image_path):
            images_to_copy.append(image_path)
        else:
            print(f"检测到空白图片，跳过处理: {image_name}")
    
    print("\n筛选完成。")
    print(f"总共找到 {len(images_to_copy)} 张非空白图片需要处理。")
    t = input()

    # 第二步：复制并重命名到 output 文件夹
    print("\n正在复制和重命名图片...")
    for i, char in enumerate(names_text):
        if i < len(images_to_copy):
            old_path = images_to_copy[i]
            ext = os.path.splitext(old_path)[1]
            new_name = f"{char}{ext}"
            new_path = os.path.join(output_folder, new_name)

            try:
                shutil.copy2(old_path, new_path)
                print(f"已将 {os.path.basename(old_path)} 复制为 {new_name}")
            except Exception as e:
                print(f"复制 {old_path} 时出错: {e}")
        else:
            print("\n文字数已用完，剩下的图片将不会被复制。")
            break

    print("\n任务完成！")
    
# 将 'your_text_here' 替换为您提供的中文字符串
text_to_use = """滂楼童雪崇朝曹南彬帽餐厅惜侧厉零雄君砯崖壑雷蜀齐焉彩划辩喻晓笨拙拟畅串歌添韵旅酒呼班盐惋怅登辽眺颔残凄尾鹤箭云泊拜臣叨秽奸岂札哉郭蕃纠呢吗劣违罢嫉憎拒李颂般腐朽唐虞汉魏兵草菅武窃羽""".replace(" ", "").replace("\n", "")

# 获取当前脚本所在的文件夹路径
current_folder = '/Users/apple/Downloads/cropped_images (2)'

process_and_copy_images(current_folder, text_to_use)
print("任务完成！")