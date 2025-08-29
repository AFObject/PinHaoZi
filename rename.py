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
text_to_use = """谈假熙凤妻惨秦卿铁涉退害刘姥妇偶厚余盛春宫德恩嫁扇晴雯丫鬟烈雀裘艺哲泽革辞苏威荷顾参黑织献茂誉章伸范轴临激障算释聪双陈哥猜芬域渥徐霞散贬诸报抒励酿透缝屋溃捧腰斩丝毫拨载叙播葆唤忆睐悖嗅踵荡陪健爆赤痕售饥饿噱拿捏盘吹驯版靡球熊摹轨饰牟诱饵启阱懂洪裹挟卖编险毁灭监措施阔遏衔逆僧陵挨戏诬钏震抚城愁访闭羹误逢饯婉赛咏姨妈谙闺细锁滴翠亭附嫌狠辣瘁卓寺请娶村座""".replace(" ", "").replace("\n", "")

# 获取当前脚本所在的文件夹路径
current_folder = '/Users/apple/Downloads/cropped_images (4)'

process_and_copy_images(current_folder, text_to_use)
print("任务完成！")