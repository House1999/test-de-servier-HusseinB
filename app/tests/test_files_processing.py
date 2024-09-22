# Built-in packages
import os
import tempfile
import unittest
from unittest.mock import call, patch

# My Custom packages
from app.utils.files_processing import create_folders_if_not_exist, fix_broken_json


class TestFilesProcessing(unittest.TestCase):
    def test_create_folders_for_valid_nested_output_file_path(self):
        output_filepath = "test_outputs/folder2/folder3/file.txt"

        with patch("os.makedirs") as mock_makedirs, patch(
            "os.path.exists", return_value=False
        ) as mock_exists:
            create_folders_if_not_exist(output_filepath)
            expected_calls = [
                call("test_outputs/"),
                call("test_outputs/folder2/"),
                call("test_outputs/folder2/folder3/"),
            ]
            mock_makedirs.assert_has_calls(expected_calls, any_order=True)

    def test_handle_no_folders_in_output_file_path(self):
        """Handles the case where only a file name is provided."""
        output_filepath = "test.json"
        with patch("os.makedirs") as mock_makedirs, patch(
            "os.path.exists", return_value=False
        ) as mock_exists:
            create_folders_if_not_exist(output_filepath)
            mock_makedirs.assert_not_called()

        # Correctly fixes and loads a JSON file with trailing commas

    def test_fix_broken_json_with_trailing_commas(self):
        broken_json_content = '{"key1": "value1", "key2": "value2",}'
        expected_output = {"key1": "value1", "key2": "value2"}

        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8"
        ) as temp_file:
            temp_file.write(broken_json_content)
            temp_filepath = temp_file.name

        try:
            result = fix_broken_json(temp_filepath)
            self.assertEqual(result, expected_output)
        finally:
            os.remove(temp_filepath)


if __name__ == "__main__":
    unittest.main()
