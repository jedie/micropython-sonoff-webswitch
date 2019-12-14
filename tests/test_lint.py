from pathlib import Path
from unittest import TestCase

from utils.main import lint_and_compile


class CodeLintTestCase(TestCase):
    def test_lint_and_compile(self):
        src_path = Path('src')
        bdist_path = Path('bdist')

        lint_and_compile(src_path, bdist_path)
