import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_links, text_to_textnodes


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

    def test_code_simple(self):
        node = TextNode("a `b` c", TextType.TEXT)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(out, [
            TextNode("a ", TextType.TEXT),
            TextNode("b", TextType.CODE),
            TextNode(" c", TextType.TEXT),
        ])

    def test_no_delimiter_noop(self):
        node = TextNode("no code", TextType.TEXT)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(out, [node])

    def test_unmatched_raises(self):
        node = TextNode("bad `code", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_bold_basic(self):
        node = TextNode("x **y** z", TextType.TEXT)
        out = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(out, [
            TextNode("x ", TextType.TEXT),
            TextNode("y", TextType.BOLD),
            TextNode(" z", TextType.TEXT),
        ])

    def test_empty_chunks_skipped(self):
        node = TextNode("****", TextType.TEXT)
        out = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(out, [])

    def test_passthrough_non_text(self):
        link = TextNode("label", TextType.LINK, "u")
        out = split_nodes_delimiter([link], "`", TextType.CODE)
        self.assertEqual(out, [link])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_links([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )
    
    def test_plain_text(self):
        nodes = text_to_textnodes("hello world")
        assert len(nodes) == 1
        assert nodes[0].text == "hello world"
        assert nodes[0].text_type == TextType.TEXT

    def test_bold_simple(self):
        nodes = text_to_textnodes("a **b** c")
        assert [n.text_type for n in nodes] == [TextType.TEXT, TextType.BOLD, TextType.TEXT]
        assert [n.text for n in nodes] == ["a ", "b", " c"]
    
    def test_italic_simple(self):
        nodes = text_to_textnodes("a _b_ c")
        assert [n.text_type for n in nodes] == [TextType.TEXT, TextType.ITALIC, TextType.TEXT]
    
    def test_code_simple(self):
        nodes = text_to_textnodes("x `y` z")
        assert [n.text_type for n in nodes] == [TextType.TEXT, TextType.CODE, TextType.TEXT]

    def test_link_simple(self):
        nodes = text_to_textnodes("see [boot](https://boot.dev)")
        assert len(nodes) == 2
        assert nodes[1].text_type == TextType.LINK
        assert nodes[1].text == "boot"
        assert nodes[1].url == "https://boot.dev"

    def test_image_simple(self):
        nodes = text_to_textnodes("pic ![alt](http://x)")
        assert nodes[-1].text_type == TextType.IMAGE
        assert nodes[-1].text == "alt"
        assert nodes[-1].url == "http://x"

    def test_mixed_inline(self):
        s = "This is **text** with an _italic_ and a `code` and a [link](u)"
        nodes = text_to_textnodes(s)
        types = [n.text_type for n in nodes]
        assert TextType.BOLD in types
        assert TextType.ITALIC in types
        assert TextType.CODE in types
        assert any(n.text_type == TextType.LINK and n.url == "u" for n in nodes)

    def test_no_emphasis_inside_code(self):
        nodes = text_to_textnodes("`**_x_**`")
        assert len(nodes) == 1
        assert nodes[0].text_type == TextType.CODE
        assert nodes[0].text == "**_x_**"

    def test_multiple_links_images(self):
        s = "[a](u1) and ![b](u2)"
        nodes = text_to_textnodes(s)
        assert any(n.text_type == TextType.LINK and n.text == "a" and n.url == "u1" for n in nodes)
        assert any(n.text_type == TextType.IMAGE and n.text == "b" and n.url == "u2" for n in nodes)

if __name__ == "__main__":
    unittest.main()