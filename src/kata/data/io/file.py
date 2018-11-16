from pathlib import Path


class FileWriter:
    @staticmethod
    def write_to_file_in_sub_path(root_dir: Path, file_sub_path: Path, file_content: str):
        def create_dir_hierarchy_if_does_not_exist():
            file_full_path.parent.mkdir(parents=True, exist_ok=True)

        def write_to_file():
            with file_full_path.open('w') as file:
                file.write(file_content)

        file_full_path = root_dir / file_sub_path
        create_dir_hierarchy_if_does_not_exist()
        write_to_file()
