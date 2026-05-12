"""
Tests for utils.py — capture_output, read_output_files.
Run with: pytest backend/tests/ -v
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import capture_output, read_output_files


class TestCaptureOutput:
    def test_captures_print_statements(self):
        def fn():
            print("hello world")

        stdout, error = capture_output(fn)
        assert "hello world" in stdout
        assert error is None

    def test_captures_exception_as_error(self):
        def fn():
            raise ValueError("test error")

        stdout, error = capture_output(fn)
        assert error is not None
        assert "test error" in error

    def test_returns_empty_string_on_no_output(self):
        def fn():
            pass

        stdout, error = capture_output(fn)
        assert stdout == ""
        assert error is None

    def test_swallows_system_exit(self):
        def fn():
            raise SystemExit(0)

        stdout, error = capture_output(fn)
        # SystemExit should not bubble up as an error
        assert error is None


class TestReadOutputFiles:
    def test_returns_empty_for_nonexistent_folder(self):
        paths, content = read_output_files("__nonexistent_module_xyz__")
        assert paths == []
        assert content == {}

    def test_reads_files_from_module_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily patch OUTPUT_ROOT
            import utils
            original = utils.OUTPUT_ROOT
            utils.OUTPUT_ROOT = tmpdir

            module_dir = os.path.join(tmpdir, "testmodule")
            os.makedirs(module_dir)
            with open(os.path.join(module_dir, "output.txt"), "w") as f:
                f.write("test content")

            paths, content = read_output_files("testmodule")

            utils.OUTPUT_ROOT = original  # restore

            assert len(paths) == 1
            assert "output.txt" in content
            assert content["output.txt"] == "test content"
