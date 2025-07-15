import kagglehub # pip install kagglehub
import shutil
import os

source_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

destination = os.path.join(os.getcwd(), "brazilian-ecommerce")
os.makedirs(destination, exist_ok=True)

shutil.copytree(source_path, destination, dirs_exist_ok=True)

print(f"Dataset: {destination}")
