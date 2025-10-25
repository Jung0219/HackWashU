import os
import shutil

# ==== CONFIG ====
SRC_DIR = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/data/general_groups"        # your source directory
DEST_DIR = "grouped_wounds"       # output directory
os.makedirs(DEST_DIR, exist_ok=True)

# ==== GROUP DEFINITIONS ====
groups = {
    "acute_wounds": [
        "abdominal-wounds", "Abrasions", "Bruises", "Cut",
        "Laceration", "Stab_wound", "surgical", "burns"
    ],
    "chronic_ulcers": [
        "diabetic_ulcers", "pressure_ulcers", "venous_ulcers",
        "leg-ulcer-images", "foot-ulcers"
    ],
    "infective_lesions": [
        "pilonidal-sinus", "epidermolysis-bullosa",
        "extravasation-wound-images", "meningitis"
    ],
    "neoplastic_lesions": [
        "malignant-wound-images", "haemangioma"
    ],
    "orthopaedic_lesions": [
        "orthopaedic-wounds", "Ingrown_nails", "toes"
    ],
}

# ==== MAIN SCRIPT ====
for group_name, folders in groups.items():
    group_dest = os.path.join(DEST_DIR, group_name)
    os.makedirs(group_dest, exist_ok=True)
    count = 1

    print(f"\n📂 Processing {group_name}...")

    for folder in folders:
        src_folder = os.path.join(SRC_DIR, folder)
        if not os.path.exists(src_folder):
            print(f"  ⚠️ Missing folder: {folder}")
            continue

        for root, _, files in os.walk(src_folder):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
                    src_path = os.path.join(root, file)
                    new_name = f"{group_name[:-1]}_{count:04d}{os.path.splitext(file)[1].lower()}"
                    dest_path = os.path.join(group_dest, new_name)
                    shutil.copy2(src_path, dest_path)
                    count += 1

    print(f"✅ {count-1} images saved to {group_name}/")

print("\n🎉 All grouping complete! Check 'grouped_wounds/' directory.")
