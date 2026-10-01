import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from yt_download.engine import EngineManager, runtime_options, compatibility_hint
from yt_download.main import create_parser
from yt_download.downloader import YTDownloader


class EngineTests(unittest.TestCase):
    def test_runtime_falls_back_from_old_deno_to_node(self):
        with patch('yt_download.engine.shutil.which', side_effect=['/deno', '/node']), \
             patch('yt_download.engine.subprocess.run', side_effect=[
                 Mock(stdout='deno 2.2.0'), Mock(stdout='v25.9.0')]):
            self.assertEqual(runtime_options(), {'js_runtimes': {'node': {'path': '/node'}}})

    def test_old_node_and_broken_runtime_rejected(self):
        with patch('yt_download.engine.shutil.which', side_effect=['/deno', '/node']), \
             patch('yt_download.engine.subprocess.run', side_effect=[
                 subprocess.TimeoutExpired('deno', 3), Mock(stdout='v20.0.0')]):
            self.assertEqual(runtime_options(), {})

    def test_cache_and_network_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = EngineManager()
            manager.cache_path = Path(directory) / 'cache.json'
            with patch('yt_download.engine.time.time', return_value=100), \
                 patch('yt_download.engine.requests.get') as get:
                get.return_value.json.return_value = {'info': {'version': '2026.9.1'}}
                self.assertEqual(manager.check_latest(), '2026.9.1')
                self.assertEqual(manager.check_latest(), '2026.9.1')
                self.assertEqual(get.call_count, 1)
            with patch('yt_download.engine.time.time', return_value=90000), \
                 patch('yt_download.engine.requests.get', side_effect=__import__('requests').Timeout) as get:
                self.assertIsNone(manager.check_latest())
                self.assertIsNone(manager.check_latest())
                self.assertEqual(get.call_count, 1)

    def test_ejs_mismatch_and_update_warning(self):
        manager = EngineManager()
        with patch('yt_download.engine.runtime_options', return_value={'js_runtimes': {'node': {}}}), \
             patch('yt_download.engine.version', return_value='0.1.0'), \
             patch('yt_download.engine.requires', return_value=['yt-dlp-ejs==0.8.0']), \
             patch.object(manager, 'check_latest', return_value='2099.1.1'):
            result = manager.diagnostics()
            self.assertFalse(result['ready'])
            self.assertEqual(len(result['warnings']), 2)

    def test_declined_update_never_runs_pip(self):
        with patch.object(EngineManager, 'check_latest', return_value=None), \
             patch('yt_download.engine.sys.stdin.isatty', return_value=True), \
             patch('yt_download.engine.Confirm.ask', return_value=False), \
             patch('yt_download.engine.subprocess.run') as run:
            self.assertFalse(EngineManager().interactive_update())
            run.assert_not_called()

    def test_confirmed_update_targets_current_python_and_venv(self):
        with patch.object(EngineManager, 'check_latest', return_value='2026.9.1'), \
             patch('yt_download.engine.sys.stdin.isatty', return_value=True), \
             patch('yt_download.engine.sys.prefix', '/venv'), \
             patch('yt_download.engine.Confirm.ask', return_value=True), \
             patch('yt_download.engine.subprocess.run', return_value=Mock(returncode=0)) as run:
            self.assertTrue(EngineManager().interactive_update())
            command = run.call_args.args[0]
            self.assertEqual(command[0], __import__('sys').executable)
            self.assertNotIn('--user', command)
            self.assertIn('yt-dlp[default]>=2026.3.17', command)

    def test_403_does_not_repeat_but_transient_error_retries(self):
        downloader = object.__new__(YTDownloader)
        downloader.max_retries = 3
        downloader.logger = Mock()
        downloader.progress_callback = None
        ydl = Mock()
        ydl.download.side_effect = RuntimeError('HTTP Error 403: Forbidden')
        with self.assertRaises(RuntimeError):
            downloader._download_with_retry(ydl, 'url')
        self.assertEqual(ydl.download.call_count, 1)
        ydl.reset_mock()
        ydl.download.side_effect = [RuntimeError('connection reset'), None]
        with patch('yt_download.downloader.time.sleep'):
            self.assertTrue(downloader._download_with_retry(ydl, 'url'))
        self.assertEqual(ydl.download.call_count, 2)

    def test_cli_and_error_hint(self):
        self.assertTrue(create_parser().parse_args(['--update-engine']).update_engine)
        self.assertIsNotNone(compatibility_hint('HTTP Error 403'))
        self.assertIsNone(compatibility_hint('No space left on device'))


if __name__ == '__main__':
    unittest.main()
