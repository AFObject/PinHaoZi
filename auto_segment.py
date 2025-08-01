# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import cv2
import numpy as np
from scipy.signal import argrelextrema, savgol_filter
import base64

app = Flask(__name__)

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

        # 根据传入的坐标裁剪图像
        cropped_img = img[top_y:bottom_y, left_x:right_x]

        # 转为灰度图并二值化
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 垂直投影
        vertical_projection = np.sum(binary, axis=0)
        
        # 1. 找到绝对零点 (投影值为0的位置)
        zero_positions = np.where(vertical_projection == 0)[0]
        
        # 2. 创建初始分割点 (所有绝对零点)
        split_positions = []
        if len(zero_positions) > 0:
            split_positions = list(zero_positions)
        
        # 3. 处理非零区域 (字符区域)
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
        
        # 4. 排序和去重
        split_positions = sorted(set(split_positions))
        
        # 5. 过滤无效分割点
        valid_splits = []
        # 这里的 `min_char_width` 应该是相对于裁剪区域的
        prev_pos = -min_char_width
        
        for pos in split_positions:
            if pos - prev_pos >= min_char_width:
                valid_splits.append(pos + left_x)  # 加上裁剪区域的左侧X坐标，返回全局坐标
                prev_pos = pos

        return valid_splits

    except Exception as e:
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
    if not data or 'image_data' not in data or 'top_y' not in data or 'bottom_y' not in data or 'left_x' not in data or 'right_x' not in data:
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
            return jsonify(result), 500
        
        return jsonify({'split_positions': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 在本地运行服务，可以根据需要更改端口
    app.run(host='0.0.0.0', port=5001, debug=True)
