import unittest
import os
from unittest.mock import Mock
from server import DiscountServicer, DiscountCodeManager


class TestDiscountServicer(unittest.TestCase):
    def setUp(self):
        self.db_path = 'db-files/test_discounts.db'
        self.servicer = DiscountServicer()
        self.servicer.code_manager = DiscountCodeManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_generate_codes(self):
        request = Mock(count=10, length=8)
        context = Mock()
        response = self.servicer.GenerateCodes(request, context)
        self.assertTrue(response.result)
        unused_codes = self.servicer.code_manager.get_unused_codes()
        self.assertEqual(len(unused_codes), 10)

    def test_use_code(self):
        # Generate a code first
        gen_request = Mock(count=1, length=8)
        self.servicer.GenerateCodes(gen_request, Mock())

        code = self.servicer.code_manager.get_unused_codes()[0]
        request = Mock(code=code)
        context = Mock()
        response = self.servicer.UseCode(request, context)
        self.assertEqual(response.result, 1)

        # Try to use the same code again
        response = self.servicer.UseCode(request, context)
        self.assertEqual(response.result, 0)


if __name__ == '__main__':
    unittest.main()