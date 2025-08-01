document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('inputText');
    const outputArea = document.getElementById('outputArea');

    // 监听输入框的输入事件
    inputText.addEventListener('input', () => {
        const text = inputText.value;
        outputArea.innerHTML = ''; // 清空之前的显示内容

        if (text.length === 0) {
            return; // 如果没有输入内容，则不显示任何图片
        }

        // 遍历输入的每一个字符
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            const img = document.createElement('img');

            // 检查字符是否是空格
            if (char === ' ') {
                // 如果是空格，创建一个透明的占位符，模拟空格效果
                img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // 1x1 透明 GIF
                img.alt = 'Space';
                img.style.width = '20px'; // 可以调整空格的宽度
                img.style.height = '60px'; // 与其他字保持相同高度
                img.style.border = 'none'; // 移除边框
                img.style.backgroundColor = 'transparent'; // 透明背景
                img.style.marginRight = '5px'; // 稍微右边距，模拟字间距
            } else {
                // 构建图片路径：假设图片都在 'handwriting_chars/' 文件夹下，以 '字.png' 命名
                img.src = `handwriting_chars/${char}.png`;
                img.alt = `找不到字：${char}.png`; // 当图片加载失败时显示此文本
                img.title = char; // 鼠标悬停时显示字符
                img.onerror = function() {
                    // 当图片加载失败时，用一个占位符来显示原始字符，帮助调试
                    this.alt = `字迹缺失: ${char}`;
                    this.style.width = '60px'; // 默认宽度
                    this.style.height = '60px'; // 默认高度
                    this.style.backgroundColor = '#ffe0b2'; // 浅橙色背景
                    this.style.color = '#e65100'; // 深橙色文字
                    this.style.border = '1px dashed #e65100'; // 虚线边框
                    this.style.textAlign = 'center';
                    this.style.lineHeight = '60px'; // 垂直居中文字
                    this.style.fontSize = '0.8em';
                    this.src = ''; // 清除错误的src，防止浏览器继续尝试加载
                };
            }
            outputArea.appendChild(img);
        }
    });
});