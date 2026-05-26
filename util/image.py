"""
图片转像素风脚本
使用方法：python image.py --input D:\PythonProject\individual\img\hk.png --output D:\PythonProject\individual\img\hk1.png --block_size 4
"""

import argparse
from PIL import Image


def convert_to_pixel_art(image_path, output_path, block_size=8):
    """
    将图片转换为像素风
    :param image_path: 输入图片路径
    :param output_path: 输出图片路径
    :param block_size: 像素块大小（数值越大像素感越强）
    """
    # 打开图片
    img = Image.open(image_path).convert("RGB")

    # 获取原始尺寸
    original_width, original_height = img.size

    # 计算缩小后的尺寸（保证至少为1x1）
    small_width = max(1, original_width // block_size)
    small_height = max(1, original_height // block_size)

    # 1. 缩小图片（每个块变成一个纯色像素）
    small_img = img.resize((small_width, small_height), Image.Resampling.NEAREST)

    # 2. 放大回原尺寸（使用NEAREST保持硬边缘）
    pixelated_img = small_img.resize((original_width, original_height), Image.Resampling.NEAREST)

    # 保存结果
    pixelated_img.save(output_path)
    print(f"✅ 像素风转换完成！\n   输入: {image_path}\n   输出: {output_path}\n   像素块大小: {block_size}px")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将图片转换为像素风（像素艺术风格）")
    parser.add_argument("--input", "-i", required=True, help="输入图片路径")
    parser.add_argument("--output", "-o", default="output_pixel.png", help="输出图片路径（默认: output_pixel.png）")
    parser.add_argument("--block_size", "-b", type=int, default=8, help="像素块大小，推荐4~16（默认: 8）")

    args = parser.parse_args()

    convert_to_pixel_art(args.input, args.output, args.block_size)

