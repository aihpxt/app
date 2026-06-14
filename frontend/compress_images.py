import os
from PIL import Image

def compress_image(input_path, output_path, quality=50):
    """压缩图片文件"""
    try:
        with Image.open(input_path) as img:
            # 转换为RGB模式（如果是RGBA）
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            # 保存压缩后的图片
            img.save(output_path, optimize=True, quality=quality)
            return True
    except Exception as e:
        print(f"压缩图片失败: {e}")
        return False

def main():
    """压缩images目录下的所有图片"""
    images_dir = "public/images"
    if not os.path.exists(images_dir):
        print(f"目录不存在: {images_dir}")
        return
    
    # 获取所有图片文件
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    for image_file in image_files:
        input_path = os.path.join(images_dir, image_file)
        output_path = os.path.join(images_dir, image_file)
        
        # 获取原始文件大小
        original_size = os.path.getsize(input_path)
        
        # 压缩图片
        if compress_image(input_path, output_path):
            # 获取压缩后的文件大小
            compressed_size = os.path.getsize(output_path)
            # 计算压缩比例
            compression_ratio = (1 - compressed_size / original_size) * 100
            print(f"压缩 {image_file}: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({compression_ratio:.1f}% 减少)")
        else:
            print(f"压缩 {image_file} 失败")

if __name__ == "__main__":
    main()