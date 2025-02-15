# used for deploy on tencent SCF

import os
from pathlib import Path
import zipfile
import shutil

def zip_project(project_dir, venv_path, zip_name):
    # 创建一个 Zip 文件
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 打包项目根目录下的文件
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)  # 保持相对路径
                zipf.write(file_path, arcname)

        # 打包 venv/Lib/site-packages 下的所有依赖
        for root, dirs, files in os.walk(venv_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, venv_path)  # 使路径从 site-packages 开始
                zipf.write(file_path, arcname)

    print(f"Project and dependencies have been zipped into {zip_name}")

# 示例调用
project_directory = Path(__file__).parent
venv_site_packages = Path(__file__).parent/'venv/Lib/site-packages'
output_zip = 'project_and_dependencies.zip'

zip_project(project_directory, venv_site_packages, output_zip)
