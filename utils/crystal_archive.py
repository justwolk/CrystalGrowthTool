import io
import os
import json
import zipfile
import tempfile
import shutil

class CrystalArchive:

    def generate_unique_path(self, directory, project_name):
        if project_name.endswith('.crystal'):
            project_name = project_name[:-8]

        crystal_file_path = os.path.join(directory, f"{project_name}.crystal")

        counter = 1
        original_name = project_name

        while os.path.exists(crystal_file_path):
            project_name = f"{original_name}_{counter}"
            crystal_file_path = os.path.join(directory, f"{project_name}.crystal")
            counter += 1

        return crystal_file_path, project_name

    def create_archive(self, folder_path, project_data, images_data):
        directory = os.path.dirname(folder_path)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with zipfile.ZipFile(folder_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                project_json = json.dumps(project_data, indent=2)
                zf.writestr('project.json', project_json)

                for idx, image_data in enumerate(images_data):
                    image_name = f'images/img_{idx + 1}.png'

                    if isinstance(image_data, str):
                        if os.path.exists(image_data):
                            zf.write(image_data, image_name)
                    elif hasattr(image_data, 'save'):
                        img_bytes = io.BytesIO()
                        image_data.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        zf.writestr(image_name, img_bytes.getvalue())
        except Exception as e:
            if os.path.exists(folder_path):
                try:
                    os.remove(folder_path)
                except:
                    pass
            raise Exception(f"Не удалось создать проект: {str(e)}")

    def load_archive(self, archive_path):
        if not zipfile.is_zipfile(archive_path):
            raise ValueError(f"Файл {archive_path} не является правильным")

        temp_dir = tempfile.mkdtemp(prefix='crystal_project_')
        images_dir = os.path.join(temp_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        with zipfile.ZipFile(archive_path, 'r') as zf:
            try:
                project_json = zf.read('project.json').decode('utf-8')
                project_data = json.loads(project_json)
            except KeyError:
                raise ValueError("Неправильный файл проекта")

            for file_info in zf.filelist:
                if file_info.filename.startswith('images/'):
                    zf.extract(file_info, temp_dir)

        return project_data, images_dir, temp_dir

    def update_archive(self, archive_path, project_data, images_dir):
        temp_path = archive_path + '.tmp'

        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            project_json = json.dumps(project_data, indent=2)
            zf.writestr('project.json', project_json)

            if os.path.exists(images_dir):  # скопировать изображения
                for filename in os.listdir(images_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(images_dir, filename)
                        zf.write(file_path, f'images/{filename}')

        # заменить оригинальный файл
        if os.path.exists(archive_path):
            os.remove(archive_path)
        os.rename(temp_path, archive_path)

    def cleanup_temp_dir(self, temp_dir):
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
