"""
Image Augmentation Script for Wound Classification Dataset
==========================================================

This script augments images in multiple subdirectories under a given input root directory.
Each subdirectory represents a class (e.g., Abrasions, Burns, Bruises, etc.).

For every class folder:
  - Original images are copied to a corresponding folder in the output directory.
  - The script generates augmented images using Albumentations until the total count
    (original + augmented) reaches a specified TARGET_COUNT.

Augmentation includes random flips, rotations, shifts, scaling, Gaussian noise, and motion blur.

Intended Use
------------
Designed for small, imbalanced medical or wound image datasets where each class
has limited samples. This script increases per-class diversity before dataset splitting.

Example Directory Structure
---------------------------
Input:
    /data/light_wounds/
        Abrasions/
        Burns/
        Bruises/
        ...

Output:
    /data/light_wounds_aug/
        Abrasions/
        Burns/
        Bruises/
        ...

Usage
-----
1. Modify `INPUT_DIR`, `OUTPUT_DIR`, and `TARGET_COUNT` as needed.
2. Run:
       python augment_all_classes.py
3. Each subdirectory will end up containing ~TARGET_COUNT images (original + augmented).

Dependencies
------------
- OpenCV (`cv2`)
- Albumentations
- tqdm

Author: Finn (with ChatGPT)
Date: October 2025
"""

import os
import cv2
import albumentations as A
from tqdm import tqdm

# ==== CONFIG ====
INPUT_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/light_wounds"
OUTPUT_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/light_wounds_aug"
TARGET_COUNT = 500  # desired total images per class (including originals)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== AUGMENTATION PIPELINE ====
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.2),
    A.Rotate(limit=15, p=0.5),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1,
                       rotate_limit=10, p=0.5),
    A.GaussNoise(var_limit=(10, 50), p=0.1),
    A.MotionBlur(blur_limit=3, p=0.2)
])


def augment_image(img):
    return transform(image=img)["image"]

# ==== AUGMENTATION LOOP PER CLASS ====


def augment_class(class_name, input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    image_files = [f for f in os.listdir(input_path) if f.lower().endswith(
        (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"))]
    current_count = len(image_files)
    print(f"\n📂 {class_name}: Found {current_count} images")

    # Copy originals first
    for file in image_files:
        src = os.path.join(input_path, file)
        dst = os.path.join(output_path, file)
        if not os.path.exists(dst):
            os.system(f'cp "{src}" "{dst}"')

    if current_count >= TARGET_COUNT:
        print(f"✅ Already has {current_count} images, skipping augmentation.")
        return

    augment_needed = TARGET_COUNT - current_count
    print(f"🔄 Augmenting {augment_needed} new images...")

    aug_per_image = max(1, augment_needed // current_count + 1)
    total_generated = 0

    for file in tqdm(image_files, desc=f"Augmenting {class_name}"):
        img_path = os.path.join(input_path, file)
        img = cv2.imread(img_path)
        if img is None:
            continue

        base_name, ext = os.path.splitext(file)
        for i in range(1, aug_per_image + 1):
            if total_generated >= augment_needed:
                break
            aug_img = augment_image(img)
            new_name = f"{base_name}_aug{i}{ext}"
            cv2.imwrite(os.path.join(output_path, new_name), aug_img)
            total_generated += 1

        if total_generated >= augment_needed:
            break

    print(f"🎉 {class_name}: Generated {total_generated} augmented images. Total now ≈ {current_count + total_generated}")

# ==== MAIN ====


def main():
    classes = [d for d in os.listdir(
        INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    for cls in classes:
        in_dir = os.path.join(INPUT_DIR, cls)
        out_dir = os.path.join(OUTPUT_DIR, cls)
        augment_class(cls, in_dir, out_dir)

    print("\n✅ All classes processed! Augmented dataset saved to:")
    print(f"   {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
