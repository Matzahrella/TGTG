import unittest
import os
import json
import shutil # For creating and removing temporary test config files/dirs
# Assuming main.py is in the parent directory of 'tests' and 'core'
# Adjust import path if main.py is structured differently or tests are run in a specific way.
# For 'python -m unittest discover tgtg-bot/tests' from project root (tgtg-bot/),
# main.py's functions need to be importable.
# This might require main.py to be structured to allow import of its functions,
# or temporarily adding its directory to sys.path for tests.
# A simpler approach for now is to place a copy of load_config or import main module.

# Let's assume main.py can be imported as a module.
# If main.py has an 'if __name__ == "__main__":' guard, its functions are importable.
import main as main_module # main refers to main.py

class TestMainConfigLoading(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory where a dummy config.json can be placed."""
        self.test_dir = "temp_test_config_dir"
        # Clean up if it exists from a previous failed run
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        self.config_file_path = os.path.join(self.test_dir, "config.json")

        # Store original working directory and change to test_dir if load_config assumes relative path from cwd
        self.original_cwd = os.getcwd()
        # For this test, we'll pass the full path to load_config, so changing cwd isn't strictly needed
        # unless load_config itself uses relative paths internally without being passed the base path.
        # The current main.py load_config takes a path, which is good.

        # Reference to the default config from main module
        self.default_config = main_module.DEFAULT_CONFIG.copy()

    def tearDown(self):
        """Clean up the temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # os.chdir(self.original_cwd) # Restore cwd if changed

    def test_load_config_valid_file(self):
        """Test loading a valid config.json file."""
        custom_settings = {
            "target_phone_numbers": ["+19998887777"],
            "base_poll_interval_seconds": 65,
            "new_custom_key": "custom_value" # load_config should keep this
        }
        with open(self.config_file_path, 'w') as f:
            json.dump(custom_settings, f)
            
        loaded_config = main_module.load_config(self.config_file_path)
        
        # Check that custom settings override defaults
        self.assertEqual(loaded_config["target_phone_numbers"], custom_settings["target_phone_numbers"])
        self.assertEqual(loaded_config["base_poll_interval_seconds"], custom_settings["base_poll_interval_seconds"])
        # Check that default settings are present if not overridden
        self.assertEqual(loaded_config["poll_interval_jitter_seconds"], self.default_config["poll_interval_jitter_seconds"])
        # Check that extra keys in user config are preserved
        self.assertEqual(loaded_config["new_custom_key"], "custom_value")


    def test_load_config_missing_file(self):
        """Test loading when config.json is missing; should return defaults."""
        # Ensure file does not exist
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)
            
        loaded_config = main_module.load_config(self.config_file_path)
        self.assertEqual(loaded_config, self.default_config)

    def test_load_config_invalid_json(self):
        """Test loading a config.json with invalid JSON content; should return defaults."""
        with open(self.config_file_path, 'w') as f:
            f.write("this is not valid json {")
            
        loaded_config = main_module.load_config(self.config_file_path)
        self.assertEqual(loaded_config, self.default_config)

    def test_load_config_some_keys_missing(self):
        """Test loading a config.json where some keys are missing; defaults should fill them."""
        partial_settings = {
            "target_phone_numbers": ["+1234567890"],
            # base_poll_interval_seconds is missing, should take default
        }
        with open(self.config_file_path, 'w') as f:
            json.dump(partial_settings, f)
            
        loaded_config = main_module.load_config(self.config_file_path)
        
        self.assertEqual(loaded_config["target_phone_numbers"], partial_settings["target_phone_numbers"])
        self.assertEqual(loaded_config["base_poll_interval_seconds"], self.default_config["base_poll_interval_seconds"])
        self.assertEqual(loaded_config["accounts_path"], self.default_config["accounts_path"])


    def test_load_config_target_phone_numbers_not_a_list(self):
        """Test if target_phone_numbers is not a list, it defaults to empty list."""
        invalid_settings = {
            "target_phone_numbers": "not_a_list_value"
        }
        with open(self.config_file_path, 'w') as f:
            json.dump(invalid_settings, f)

        loaded_config = main_module.load_config(self.config_file_path)
        # Check if this specific key was reverted to default due to type mismatch
        self.assertEqual(loaded_config["target_phone_numbers"], self.default_config["target_phone_numbers"])
        # Check other keys are still loaded if they were valid or defaulted
        self.assertEqual(loaded_config["base_poll_interval_seconds"], self.default_config["base_poll_interval_seconds"])


# To make `import main as main_module` work, ensure:
# 1. `main.py` is in the `tgtg-bot/` directory.
# 2. The tests are run from the `tgtg-bot/` directory (e.g., `python -m unittest discover tests`).
# 3. `tgtg-bot/` directory is effectively on Python's path, or `main.py` is structured
#    as a module that can be imported.
#    If `main.py` has code outside functions or `if __name__ == "__main__":`,
#    importing it might execute that code. It's best if main.py's logic is encapsulated.

if __name__ == '__main__':
    unittest.main()

```
