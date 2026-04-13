import os
import sys
import unittest
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.services.file_service import file_url

class TestFixes(unittest.TestCase):
    def test_file_url_none(self):
        # Testing the crash fix
        self.assertEqual(file_url(None), "")
        self.assertEqual(file_url(""), "")
        self.assertEqual(file_url("uploads\\test.pdf"), "/uploads/test.pdf")
        print("✅ file_url validation passed.")

if __name__ == "__main__":
    unittest.main()
