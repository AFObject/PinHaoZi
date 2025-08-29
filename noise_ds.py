import cv2
import numpy as np
import os
import glob
import argparse

def remove_noise(image_path, output_path, threshold=200, contrast_factor=1.5):
    """
    去除噪点并增强对比度，保留黑色原貌
    参数:
        image_path: 输入图片路径
        output_path: 输出图片路径
        threshold: 噪点阈值 (0-255)
        contrast_factor: 对比度增强因子 (>1)
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 创建噪点掩膜 - 识别灰色噪点
    # 低于此值的像素视为有效文字，高于此值的像素视为噪点
    _, noise_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # 反转噪点掩膜：噪点区域为白色(255)，文字区域为黑色(0)
    noise_mask_inv = cv2.bitwise_not(noise_mask)
    
    # 增强对比度 - 使用线性变换
    # 公式: output = alpha*input + beta
    # 这里alpha控制对比度，beta控制亮度
    enhanced = cv2.convertScaleAbs(gray, alpha=contrast_factor, beta=0)
    
    # 组合图像：在文字区域使用增强后的图像，在噪点区域使用白色
    # 1. 提取文字区域（从增强图像中取噪点掩膜反转的区域）
    text_region = cv2.bitwise_and(enhanced, enhanced, mask=noise_mask_inv)
    
    # 2. 创建纯白色背景
    white_background = np.full_like(gray, 255)
    
    # 3. 在噪点区域使用白色背景
    clean_background = cv2.bitwise_and(white_background, white_background, mask=noise_mask)
    
    # 4. 合并文字区域和清洁背景
    result = cv2.add(text_region, clean_background)
    
    # 保存结果
    cv2.imwrite(output_path, result)
    return result

def batch_denoise(input_dir, output_dir, threshold=200, contrast_factor=1.5):
    """
    批量处理图片
    参数:
        input_dir: 输入文件夹
        output_dir: 输出文件夹
        threshold: 噪点阈值 (0-255)
        contrast_factor: 对比度增强因子 (>1)
    """
    # 创建输出文件夹
    os.makedirs(output_dir, exist_ok=True)
    
    # 支持的图片格式
    img_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    files = []
    for fmt in img_formats:
        files.extend(glob.glob(os.path.join(input_dir, f'*.{fmt}')))
        files.extend(glob.glob(os.path.join(input_dir, f'*.{fmt.upper()}')))
    
    if not files:
        print(f"在 {input_dir} 中未找到图片文件")
        return
    
    print(f"开始处理 {len(files)} 张图片...")
    print(f"参数设置: 噪点阈值={threshold}, 对比度增强={contrast_factor}")
    
    for i, img_path in enumerate(files):
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        
        remove_noise(img_path, output_path, threshold, contrast_factor)
        print(f"处理进度: {i+1}/{len(files)} - {filename}")
    
    print(f"\n处理完成！结果已保存至 {output_dir}")

def main():
    # 创建命令行参数解析器
    # parser = argparse.ArgumentParser(description='书法图片去噪工具')
    # parser.add_argument('-i', '--input', type=str, default='input_images', 
    #                     help='输入文件夹路径 (默认: input_images)')
    # parser.add_argument('-o', '--output', type=str, default='output', 
    #                     help='输出文件夹路径 (默认: output)')
    # parser.add_argument('-t', '--threshold', type=int, default=200, 
    #                     help='噪点阈值 (0-255, 默认: 200)')
    # parser.add_argument('-c', '--contrast', type=float, default=1.5, 
    #                     help='对比度增强因子 (默认: 1.5)')
    
    # args = parser.parse_args()
    
    # 运行批量处理
    # batch_denoise(
    #     input_dir=args.input,
    #     output_dir=args.output,
    #     threshold=args.threshold,
    #     contrast_factor=args.contrast
    # )
    batch_denoise(
        input_dir='/Users/apple/Downloads/cropped_images (2)/output',
        output_dir='/Users/apple/Downloads/cropped_images (2)/output_d',
        threshold=255,
        contrast_factor=1.2
    )

if __name__ == "__main__":
    main()