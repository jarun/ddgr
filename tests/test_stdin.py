import io
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'ddgr'))
command = module['DdgCmd']


class InputStream(io.StringIO):
    @property
    def encoding(self):
        return 'utf-8'

    def __init__(self, value='', terminal=False):
        super().__init__(value)
        self.terminal = terminal

    def isatty(self):
        return self.terminal

    def fileno(self):
        return 0


class StdinTests(unittest.TestCase):
    def test_url_handler_inherits_stdin(self):
        open_url = module['open_url']
        process = MagicMock()
        with patch.object(open_url, 'url_handler', 'pyreader', create=True), \
             patch.dict(open_url.__globals__, {'Popen': process}):
            open_url('https://example.com')

        process.assert_called_once_with(['pyreader', 'https://example.com'])
        process.return_value.__enter__.return_value.communicate.assert_called_once_with()

    def run_main(self, args, stdin, stdout_terminal=False, terminal_error=None):
        with patch.object(sys, 'argv', ['ddgr', *args]), \
             patch.object(sys, 'stdin', stdin), \
             patch.object(sys, 'stdout', InputStream(terminal=stdout_terminal)), \
               patch.object(sys, 'stderr', InputStream()), \
             patch.object(module['os'], 'open', side_effect=terminal_error, return_value=42) as open_terminal, \
             patch.object(module['os'], 'dup2') as dup_terminal, \
             patch.object(module['os'], 'close') as close_terminal, \
             patch.object(command, 'fetch', autospec=True) as fetch, \
             patch.object(command, 'display_instant_answer'), \
             patch.object(command, 'display_results') as display, \
             patch.object(command, 'cmdloop', autospec=True) as cmdloop:
            try:
                module['main']()
            except SystemExit as error:
                self.assertEqual(error.code, 0)
            return fetch, display, cmdloop, open_terminal, dup_terminal, close_terminal

    def test_pipe_searches_once_without_prompt(self):
        fetch, display, cmdloop, _, _, _ = self.run_main([], InputStream('hello\n  world\n'))
        self.assertEqual(fetch.call_args.args[0].keywords, ['hello', 'world'])
        display.assert_called_once()
        cmdloop.assert_not_called()

    def test_pipe_restores_terminal_for_repl(self):
        fetch, _, cmdloop, open_terminal, dup_terminal, close_terminal = self.run_main(
            [], InputStream('q\n'), stdout_terminal=True)
        fetch.assert_not_called()
        self.assertEqual(cmdloop.call_args.args[0].keywords, ['q'])
        open_terminal.assert_called_once_with('/dev/tty', module['os'].O_RDONLY)
        dup_terminal.assert_called_once_with(42, 0)
        close_terminal.assert_called_once_with(42)

    def test_terminal_unavailable_falls_back_to_one_search(self):
        fetch, _, cmdloop, _, _, _ = self.run_main(
            [], InputStream('hello'), stdout_terminal=True, terminal_error=OSError())
        fetch.assert_called_once()
        cmdloop.assert_not_called()

    def test_noninteractive_flags_do_not_restore_terminal(self):
        for flag in ('--noprompt', '--json', '--instant', '--ducky'):
            with self.subTest(flag=flag):
                _, display, cmdloop, open_terminal, _, _ = self.run_main(
                    [flag], InputStream('hello'), stdout_terminal=True)
                cmdloop.assert_not_called()
                open_terminal.assert_not_called()
                if flag == '--json':
                    self.assertTrue(display.call_args.kwargs['json_output'])

    def test_empty_pipe_fails_without_prompting(self):
        with patch.object(sys, 'argv', ['ddgr']), \
             patch.object(sys, 'stdin', InputStream(' \n')), \
             patch.object(sys, 'stdout', InputStream()), \
               patch.dict(module['main'].__globals__, {'LOGERR': lambda error: None}), \
             patch.object(command, 'cmdloop') as cmdloop:
            with self.assertRaises(SystemExit) as error:
                module['main']()
            self.assertEqual(error.exception.code, 1)
            cmdloop.assert_not_called()

    def test_command_line_keywords_leave_stdin_for_repl(self):
        stdin = InputStream('q\n')
        _, _, cmdloop, open_terminal, _, _ = self.run_main(['hello'], stdin)
        self.assertEqual(cmdloop.call_args.args[0].keywords, ['hello'])
        self.assertEqual(stdin.read(), 'q\n')
        open_terminal.assert_not_called()

    def test_spawn_searches_keywords_without_reading_stdin(self):
        for flag in ('-s', '--spawn'):
            with self.subTest(flag=flag):
                stdin = InputStream('ignored')
                with patch.object(stdin, 'read', side_effect=AssertionError('stdin was read')):
                    fetch, _, cmdloop, open_terminal, _, _ = self.run_main(
                        [flag, 'hello', 'world'], stdin, stdout_terminal=True)
                self.assertEqual(fetch.call_args.args[0].keywords, ['hello', 'world'])
                cmdloop.assert_not_called()
                open_terminal.assert_not_called()

    def test_spawn_without_keywords_does_not_wait_for_stdin(self):
        executable = str(Path(__file__).resolve().parents[1] / 'ddgr')
        for flag in ('-s', '--spawn'):
            with self.subTest(flag=flag):
                process = subprocess.Popen([sys.executable, executable, flag], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    self.assertEqual(process.wait(timeout=3), 1)
                    self.assertIn(b'No keywords', process.stderr.read())
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                    process.stdin.close()
                    process.stdout.close()
                    process.stderr.close()

    def test_terminal_stdin_starts_repl(self):
        _, _, cmdloop, open_terminal, _, _ = self.run_main([], InputStream(terminal=True))
        cmdloop.assert_called_once()
        open_terminal.assert_not_called()


if __name__ == '__main__':
    unittest.main()