# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS # 导入 CORS 模块
import cv2
import numpy as np
from scipy.signal import argrelextrema, savgol_filter
import base64
import matplotlib
# 使用非交互式 Agg 后端，以避免在非主线程中创建 GUI 窗口的错误
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)
CORS(app) # 初始化 CORS，允许所有来源的跨域请求

# 设置 Matplotlib 支持中文
plt.rcParams['font.sans-serif'] = ['Songti SC']
plt.rcParams['axes.unicode_minus'] = False

# 定义日志文件夹
LOG_DIR = 'logs'

# 定义一个可以被外部调用的核心分割函数
def get_vertical_split_positions(img_data, top_y, bottom_y, left_x, right_x, min_char_width=25, max_char_width=45):
    """
    基于投影零点和局部最小值在给定区域内进行字符分割。

    参数:
    img_data (bytes): 图像的原始字节数据。
    top_y (int): 裁剪区域的顶部Y坐标。
    bottom_y (int): 裁剪区域的底部Y坐标。
    left_x (int): 裁剪区域的左侧X坐标。
    right_x (int): 裁剪区域的右侧X坐标。
    min_char_width (int): 最小字符宽度(像素)。
    max_char_width (int): 最大字符宽度(像素)。

    返回:
    list: 垂直分割线的横坐标数组。
    """
    try:
        # 解码 Base64 字符串为图像
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {'error': '无法解码图像数据'}, 400
        
        # 添加日志：打印原始图像的尺寸
        print(f"原始图像尺寸: {img.shape}")

        # 根据传入的坐标裁剪图像
        cropped_img = img[top_y:bottom_y, left_x:right_x]
        
        # 添加日志：打印裁剪区域的坐标和新图像尺寸
        print(f"裁剪区域: top_y={top_y}, bottom_y={bottom_y}, left_x={left_x}, right_x={right_x}")
        print(f"裁剪后的图像尺寸: {cropped_img.shape}")
        
        # 检查裁剪后的图像是否为空
        if cropped_img.shape[0] == 0 or cropped_img.shape[1] == 0:
            return {'error': '裁剪区域无效，图像为空'}, 400

        # 转为灰度图并二值化
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 垂直投影
        vertical_projection = np.sum(binary, axis=0)
        
        # 1. 找到所有连续的绝对零点区域
        zero_positions = np.where(vertical_projection == 0)[0]
        zero_runs = []
        if len(zero_positions) > 0:
            # 找到连续零点的索引差值不为1的位置
            diffs = np.diff(zero_positions, prepend=zero_positions[0]-1)
            split_indices = np.where(diffs > 1)[0]
            
            # 从这些索引中提取连续零点区域
            current_start = 0
            for split_idx in split_indices:
                zero_runs.append((zero_positions[current_start], zero_positions[split_idx-1]))
                current_start = split_idx
            zero_runs.append((zero_positions[current_start], zero_positions[-1]))
            
        split_positions = []
        for start, end in zero_runs:
            length = end - start
            if length < 15:
                # 区域不长，取中点作为断点
                split_positions.append(start + length // 2)
            else:
                # 区域长，取两侧端点作为断点
                split_positions.append(start)
                split_positions.append(end)

        
        # 2. 处理非零区域 (字符区域)
        in_char = False
        char_start = 0
        
        for x in range(binary.shape[1]):
            # 进入字符区域
            if vertical_projection[x] > 0 and not in_char:
                in_char = True
                char_start = x
            
            # 离开字符区域
            elif vertical_projection[x] == 0 and in_char:
                in_char = False
                char_width = x - char_start
                
                # 检查字符宽度是否超出预期范围
                if char_width > max_char_width:
                    char_region = vertical_projection[char_start:x]
                    
                    # 策略1: 优先找绝对零点
                    local_zeros = np.where(char_region == 0)[0] + char_start
                    if len(local_zeros) > 0:
                        split_positions.extend(local_zeros)
                    # 策略2: 没有零点则找局部最小值点
                    else:
                        center = char_start + char_width // 2
                        min_len_for_savgol = 5
                        
                        if len(char_region) >= min_len_for_savgol:
                            window_length = min(11, len(char_region) - (len(char_region)%2==0))
                            if window_length < 3:
                                window_length = 3
                            
                            polyorder = min(3, window_length - 1)

                            smoothed_char_region = savgol_filter(char_region.astype(float), window_length=window_length, polyorder=polyorder)
                            local_min_indices = argrelextrema(smoothed_char_region, np.less, order=1)[0]
                            
                            local_min_positions = local_min_indices + char_start
                            
                            if len(local_min_positions) > 0:
                                threshold_val = 2000
                                valid_local_min_positions = [pos for i, pos in enumerate(local_min_positions) if smoothed_char_region[pos - char_start] <= threshold_val]
                                
                                if len(valid_local_min_positions) > 0:
                                    closest = min(valid_local_min_positions, key=lambda pos: abs(pos - center))
                                    split_positions.append(closest)
                                else:
                                    # 回退到原始的全局最小值逻辑
                                    min_val = np.min(char_region)
                                    min_positions = np.where(char_region == min_val)[0] + char_start
                                    if len(min_positions) > 0:
                                        closest = min(min_positions, key=lambda pos: abs(pos - center))
                                        split_positions.append(closest)
                            else:
                                # 回退到原始的全局最小值逻辑
                                min_val = np.min(char_region)
                                min_positions = np.where(char_region == min_val)[0] + char_start
                                if len(min_positions) > 0:
                                    closest = min(min_positions, key=lambda pos: abs(pos - center))
                                    split_positions.append(closest)
                        else:
                            min_val = np.min(char_region)
                            min_positions = np.where(char_region == min_val)[0] + char_start
                            if len(min_positions) > 0:
                                closest = min(min_positions, key=lambda pos: abs(pos - center))
                                split_positions.append(closest)
        
        # 3. 排序和去重
        split_positions = sorted(set(split_positions))
        
        # 4. 过滤无效分割点
        valid_splits = []
        # 这里的 `min_char_width` 应该是相对于裁剪区域的
        prev_pos = -min_char_width
        
        for pos in split_positions:
            if pos - prev_pos >= min_char_width:
                # 加上裁剪区域的左侧X坐标，返回全局坐标
                # 确保将 np.int64 转换为 Python int，以避免 JSON 序列化错误
                valid_splits.append(int(pos + left_x))
                prev_pos = pos
        
        # 5. 可视化和日志记录
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_filename = f"segmentation_log_{timestamp}.png"
        log_filepath = os.path.join(LOG_DIR, log_filename)
        
        plt.figure(figsize=(10, 15))
        
        # 子图1: 原始图像
        plt.subplot(3, 1, 1)
        plt.imshow(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
        plt.title('原始图像')
        
        # 子图2: 二值化图像
        plt.subplot(3, 1, 2)
        plt.imshow(binary, cmap='gray')
        plt.title('二值化后图像')
        
        # 子图3: 垂直投影曲线和分割点
        plt.subplot(3, 1, 3)
        plt.plot(vertical_projection, label='投影值')
        
        # 将分割点坐标转换为相对于裁剪区域的坐标
        relative_splits = [pos - left_x for pos in valid_splits]
        for split_x in relative_splits:
            plt.axvline(x=split_x, color='r', linestyle='--', label='分割点' if split_x == relative_splits[0] else "")
            
        plt.title('垂直投影随 x 轴变化曲线')
        plt.xlabel('x 轴位置')
        plt.ylabel('投影值')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(log_filepath)
        # 如果需要本地调试时实时显示图像，可以取消下一行的注释
        # plt.show()
        plt.close()
        
        print(f"日志图像已保存到: {log_filepath}")
        
        # 添加日志：打印最终找到的分割点
        print(f"原始分割点: {split_positions}")
        print(f"找到 {len(valid_splits)} 个有效分割点。")
        print(f"分割点位置: {valid_splits}")

        return valid_splits

    except Exception as e:
        # 添加日志：打印详细的异常信息
        print(f"在get_vertical_split_positions函数中发生异常: {e}")
        return {'error': str(e)}, 500

@app.route('/segment', methods=['POST'])
def segment_image():
    """
    处理 POST 请求，对图片进行自动分割。
    请求体应为 JSON 格式:
    {
        "image_data": "<base64_encoded_image_string>",
        "top_y": 0,
        "bottom_y": 100,
        "left_x": 0,
        "right_x": 200
    }
    """
    data = request.json
    
    # 添加日志：打印收到的请求体
    print("收到 /segment POST请求。")
    print(f"请求数据: {data.keys()}")

    if not data or 'image_data' not in data or 'top_y' not in data or 'bottom_y' not in data or 'left_x' not in data or 'right_x' not in data:
        print("错误: 无效的请求体。")
        return jsonify({'error': '无效的请求体'}), 400

    try:
        # 从 JSON 中获取数据
        image_data_base64 = data['image_data'].split(',')[1] # 移除 data:image/png;base64,
        image_bytes = base64.b64decode(image_data_base64)
        top_y = data['top_y']
        bottom_y = data['bottom_y']
        left_x = data['left_x']
        right_x = data['right_x']
        
        min_char_width = data.get('min_char_width', 30)
        max_char_width = data.get('max_char_width', 50)
        
        # 调用核心分割函数
        result = get_vertical_split_positions(
            image_bytes, 
            top_y, 
            bottom_y, 
            left_x, 
            right_x,
            min_char_width,
            max_char_width
        )
        
        if isinstance(result, dict) and 'error' in result:
            print(f"核心分割函数返回错误: {result['error']}")
            return jsonify(result), 500
        
        print(f"成功处理请求。返回 {len(result)} 个分割点。")
        return jsonify({'split_positions': result}), 200

    except Exception as e:
        print(f"在segment_image函数中发生异常: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 在本地运行服务，可以根据需要更改端口
    app.run(host='0.0.0.0', port=5001, debug=True)
