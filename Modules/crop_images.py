import os
from PIL import Image

def crop_images(folder_path, do_crop):
    crop_box = (136, 6, 136 + 721, 6 + 721)
    cropped_images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img_path = os.path.join(folder_path, filename)
            img = Image.open(img_path)
            if do_crop:
                cropped_img = img.crop(crop_box)
            else:
                cropped_img = img
            cropped_images.append(cropped_img)

    return cropped_images
