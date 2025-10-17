import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_node_works(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node_2", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url_none(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        self.assertEqual(node.url, None)

    def test_different_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.DEFAULT)
        self.assertNotEqual(node.text_type, node2.text_type)

    #def different_properties(self):



if __name__ == "__main__":
    unittest.main()