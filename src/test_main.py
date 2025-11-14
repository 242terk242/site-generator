import unittest

from main import extract_title, generate_page

class TestTextNode(unittest.TestCase):

    def tet_single_h1_trimmed(self):
        markdown = "# Hello World "
        result = extract_title(markdown)
        self.assertEqual(result, "Hello World")

    def test_single_h1_trimmed(self):
        markdown = " Hello World " \
        "# Title"
        result = extract_title(markdown)
        self.assertEqual(result, "Tile")
    
    def test_multiple_headers(self):
        markdown = " Hello World " \
        "## Title" \
        "### Title" \
        "# theRightTitle"
        result = extract_title(markdown)
        self.assertEqual(result, "theRightTitle")

    def test_multiple_headers(self):
        markdown = " Hello World " \
        "## Title" \
        "### Title" \
        " theRightTitle"
        result = extract_title(markdown)
        self.assertRaises(Exception("No header in markdown"), result)
