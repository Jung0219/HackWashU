import os
import random
import shutil
from math import floor
from tqdm import tqdm

# ==== CONFIG ====
SOURCE_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/light_wounds_aug"
DEST_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/training"
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.7, 0.15, 0.15
BALANCE_TEST = True
SEED = 42
random.seed(SEED)

# ==== FUNCTIONS ====


def make_dirs(base, classes):
    for split in ["train", "val", "test"]:
        for cls in classes:
            os.makedirs(os.path.join(base, split, cls), exist_ok=True)


def copy_files(file_list, dest_dir, class_name):
    for f in file_list:
        dest_path = os.path.join(dest_dir, class_name, os.path.basename(f))
        shutil.copy2(f, dest_path)


def split_class(class_path):
    images = [
        os.path.join(class_path, f)
        for f in os.listdir(class_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"))
    ]
    random.shuffle(images)
    n_total = len(images)
    n_train = floor(n_total * TRAIN_RATIO)
    n_val = floor(n_total * VAL_RATIO)
    train = images[:n_train]
    val = images[n_train:n_train + n_val]
    test = images[n_train + n_val:]
    return train, val, test


# ==== MAIN SCRIPT ====
def main():
    classes = [d for d in os.listdir(SOURCE_DIR)
               if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    make_dirs(DEST_DIR, classes)

    print("📂 Splitting dataset...")
    splits = {"train": {}, "val": {}, "test": {}}
    summary = {}

    for cls in classes:
        class_path = os.path.join(SOURCE_DIR, cls)
        train, val, test = split_class(class_path)
        splits["train"][cls] = train
        splits["val"][cls] = val
        splits["test"][cls] = test
        summary[cls] = {"train": len(
            train), "val": len(val), "test": len(test)}
        print(f"  {cls}: train={len(train)}, val={len(val)}, test={len(test)}")

    # ===== Balance the test set =====
    if BALANCE_TEST:
        min_test = min(len(splits["test"][cls]) for cls in classes)
        print(f"\n⚖️ Balancing test set to {min_test} samples per class")
        for cls in classes:
            test_files = splits["test"][cls]
            if len(test_files) > min_test:
                test_files = random.sample(test_files, min_test)
            splits["test"][cls] = test_files
            summary[cls]["test"] = len(test_files)

    print("\n📤 Copying files...")
    for split in ["train", "val", "test"]:
        for cls in tqdm(classes, desc=f"Copying {split}"):
            dest_dir = os.path.join(DEST_DIR, split)
            copy_files(splits[split][cls], dest_dir, cls)

    print("\n✅ Dataset split complete!\n")
    print("📊 Summary of images per class:")
    print("-" * 60)
    print(f"{'Class':25s} {'Train':>8} {'Val':>8} {'Test':>8} {'Total':>8}")
    print("-" * 60)
    for cls, counts in summary.items():
        total = counts["train"] + counts["val"] + counts["test"]
        print(
            f"{cls:25s} {counts['train']:8d} {counts['val']:8d} {counts['test']:8d} {total:8d}")
    print("-" * 60)
    total_train = sum(summary[c]["train"] for c in summary)
    total_val = sum(summary[c]["val"] for c in summary)
    total_test = sum(summary[c]["test"] for c in summary)
    print(f"{'TOTAL':25s} {total_train:8d} {total_val:8d} {total_test:8d} {total_train + total_val + total_test:8d}")
    print("-" * 60)
    print(f"\nOutput structure saved under: {DEST_DIR}")


if __name__ == "__main__":
    main()
