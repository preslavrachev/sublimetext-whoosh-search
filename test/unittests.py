import os
import sys
import unittest

TEST_FOLDER_PATH = '/test_folder'

stubs_dir = os.path.join(os.path.dirname(__file__), "stubs")
if stubs_dir not in sys.path:
    sys.path.append(stubs_dir)

import WhooshSearch


class Object:
    pass


class WhooshSearchTest(unittest.TestCase):

    # The usual first unit test. Just to check if it works
    def test_two_plus_two(self):
        self.assertEqual(2 + 2, 4)

    def test_target_dir_extraction_for_windows_commands(self):
        class TestWindowCommand(WhooshSearch.BaseCommand):
            def __init__(self):
                self.window = __create_a_mock_window_object__()

        test_window_command = TestWindowCommand()
        target_dir = test_window_command.get_target_dir()

        self.assertEqual(target_dir, TEST_FOLDER_PATH)

    def test_target_dir_extraction_for_text_commands(self):
        class TestTextCommand(WhooshSearch.BaseCommand):
            def __init__(self):
                self.view = Object()
                self.view.window = lambda: __create_a_mock_window_object__()

        test_text_command = TestTextCommand()
        target_dir = test_text_command.get_target_dir()

        self.assertEqual(target_dir, TEST_FOLDER_PATH)


# Helper functions
def __create_a_mock_window_object__():
    window = Object()
    window.folders = lambda: [TEST_FOLDER_PATH]
    return window
