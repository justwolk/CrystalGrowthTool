import os
import warnings
from PIL import Image


def init_images(image_folder, do_crop=True):
    
    image_files = []
    for file in os.listdir(image_folder):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            image_files.append(file)
    
    image_files.sort()
    
    processed_images = []
    crop_box = (136, 6, 136 + 721, 6 + 721)  
    # по пикселям высчитано, как обрезать, чтобы из оригинального снимка с АСМ обрезать до ровного квадрата для последующей обработки

    for file in image_files:
        file_path = os.path.join(image_folder, file)
        try:
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                                
                if do_crop:
                    cropped_img = img.crop(crop_box)
                    processed_images.append(cropped_img.copy())
                else:
                    processed_images.append(img.copy())
                    
        except Exception as e:
            print(f"Ошибка обработки изображения {file}: {e}")
            continue
    
    return processed_images
