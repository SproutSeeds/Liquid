import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

# These tests exercise configuration without installing data-science packages.
with patch.dict(sys.modules, {'pandas': types.ModuleType('pandas')}):
    from app_state import AppState
from settings_management import save_settings


class SecretStorageTests(unittest.TestCase):
    def test_clean_checkout_loads_nonsecret_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            defaults = {'fred_api_key': '', 'trader_made_api_key': '',
                        'graphing_start_date': '2020-01-01'}
            (root / 'settings.example.json').write_text(json.JSONEncoder().encode(defaults))
            state = AppState.__new__(AppState)
            state.load_default_settings(str(root / 'settings.json'))
            self.assertEqual(state.graphing_start_date, '2020-01-01')
            self.assertEqual(state.fred_api_key, '')
            self.assertEqual(state.trader_made_api_key, '')

    def test_environment_secret_is_not_persisted_by_save(self):
        secret = secrets.token_hex(16)
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'settings.json'
            state = AppState.__new__(AppState)
            state.config_file = str(config)
            state.fred_api_key = ''
            state.trader_made_api_key = ''
            with patch.dict(os.environ, {'FRED_API_KEY': secret,
                                         'TRADERMADE_API_KEY': secret}):
                self.assertEqual(state.get_fred_api_key(), secret)
                self.assertEqual(state.get_trader_made_api_key(), secret)
                state.save_state()
            self.assertNotIn(secret, config.read_text())

    def test_saved_settings_replace_public_file_with_private_file(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'settings.json'
            config.write_text('{}')
            config.chmod(0o644)
            save_settings(str(config), {'fred_api_key': secrets.token_hex(16)})
            self.assertIn('fred_api_key', json.loads(config.read_text()))
            if os.name == 'posix':
                self.assertEqual(config.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(Path(directory).glob('.settings-*')), [])


if __name__ == '__main__':
    unittest.main()
