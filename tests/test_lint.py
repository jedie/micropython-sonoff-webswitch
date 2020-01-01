from unittest import TestCase

from utils.main import lint_and_compile


class CodeLintTestCase(TestCase):
    def test_lint_and_compile(self):
        lint_and_compile()
