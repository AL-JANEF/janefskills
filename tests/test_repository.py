from __future__ import annotations

import unittest

from scripts.validate import validate


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_contract(self) -> None:
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
