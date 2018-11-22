from pathlib import Path

import pytest
import yaml

from kata.data.io.file import FileWriter


class TestFileWriter:
    @pytest.fixture
    def file_writer(self):
        return FileWriter()

    class TestWriteToFileInSubPath:
        # Already covered by tests in 'test_grepo'
        # If adding functionality to the FileWriter specifically add tests here
        pass

    class TestWriteYamlToFile:
        def test_valid_yaml(self, tmp_path: Path, file_writer: FileWriter):
            # Given: A file path and valid yaml data
            file_path = tmp_path / 'file.yaml'
            valid_yaml_data = {'FirstKey': {'SubKey': 44},
                               'SecondKey': {'AList': ['element1', 'element2']}}

            # When: Writing yaml data to file
            file_writer.write_yaml_to_file(file_path, valid_yaml_data)

            # Then: File has been correctly written
            with file_path.open('r') as f:
                assert yaml.load(f.read()) == valid_yaml_data
