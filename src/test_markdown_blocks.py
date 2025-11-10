import unittest

from markdown_blocks import BlockType, markdown_to_blocks, block_to_block_type, markdown_to_html_node
from src.htmlnode import LeafNode, HTMLNode, ParentNode

class TestBlockMarkdown(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_empty_string(self):
        assert markdown_to_blocks("") == []

    def test_single_paragraph_trims_and_collapses_whitespace(self):
        md = "  Hello world   "
        assert markdown_to_blocks(md) == ["Hello world"]

    def test_multiple_paragraphs_split_on_blank_lines(self):
        md = "A\n\nB\n\nC"
        assert markdown_to_blocks(md) == ["A", "B", "C"]

    def test_paragraph_with_internal_blank_lines_kept_in_block(self):
        md = "A line\n\n\nstill same block?"
        # Decide your spec:
        # If two+ blank lines split blocks, expect ["A line", "still same block?"]
        assert markdown_to_blocks(md) == ["A line", "still same block?"]

    def test_headings_preserve_lines_until_blank(self):
        md = "# Title\nMore\n\nNext"
        assert markdown_to_blocks(md) == ["# Title\nMore", "Next"]

    def test_code_fence_block(self):
        md = "Before\n\n```js\nconsole.log(1)\n```\n\nAfter"
        assert markdown_to_blocks(md) == ["Before", "```js\nconsole.log(1)\n```", "After"]

    def test_unclosed_code_fence_treated_as_until_eof(self):
        md = "```py\nx=1"
        assert markdown_to_blocks(md) == ["```py\nx=1"]

    def test_list_block_bullets_grouped(self):
        md = "- a\n- b\n- c\n\nNext"
        assert markdown_to_blocks(md) == ["- a\n- b\n- c", "Next"]

    def test_numbered_list_block_grouped(self):
        md = "1. a\n2. b\n\nEnd"
        assert markdown_to_blocks(md) == ["1. a\n2. b", "End"]

    #def test_mixed_list_breaks_blocks(self):
        #md = "- a\n1. b\n- c"
        # Decide spec: either split at style change or keep contiguous list lines.
        #assert markdown_to_blocks(md) == ["- a", "1. b", "- c"]

    def test_blockquote_block_grouping(self):
        md = "> a\n> b\n\nc"
        assert markdown_to_blocks(md) == ["> a\n> b", "c"]

    def test_trailing_and_leading_blank_lines_ignored(self):
        md = "\n\nA\n\n"
        assert markdown_to_blocks(md) == ["A"]

    def test_hr_block(self):
        md = "Before\n\n---\n\nAfter"
        assert markdown_to_blocks(md) == ["Before", "---", "After"]

    def test_heading_basic(self):
        assert block_to_block_type("# Title") == BlockType.HEADING

    def test_heading_no_space_is_paragraph(self):
        assert block_to_block_type("#NoSpace") == BlockType.PARAGRAPH

    def test_code_fenced(self):
        block = "```\nprint('x')\n```"
        assert block_to_block_type(block) == BlockType.CODE

    def test_code_missing_closing_is_paragraph(self):
        block = "```\nprint('x')"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_quote_all_lines_prefixed(self):
        block = ">\n> quoted\n> more"
        assert block_to_block_type(block) == BlockType.QUOTE

    def test_quote_one_line_missing_prefix_is_paragraph(self):
        block = ">\nnot quoted\n>"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_unordered_list_valid(self):
        block = "- a\n- b\n- c"
        assert block_to_block_type(block) == BlockType.UNORDERED_LIST

    def test_unordered_list_missing_space_is_paragraph(self):
        block = "- a\n-item"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_ordered_list_valid_sequence(self):
        block = "1. one\n2. two\n3. three"
        assert block_to_block_type(block) == BlockType.ORDERED_LIST

    def test_ordered_list_out_of_order_is_paragraph(self):
        block = "1. one\n3. two\n2. three"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_ordered_list_missing_space_is_paragraph(self):
        block = "1.one\n2. two"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_paragraph_fallback(self):
        assert block_to_block_type("just some text") == BlockType.PARAGRAPH

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
    
    def test_headings(self):
        md = """
# This is an h1

## This is an h2 with **bold**

### This is an h3 with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><h1>This is an h1</h1><h2>This is an h2 with <b>bold</b></h2><h3>This is an h3 with <i>italic</i></h3></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> with multiple lines
> and **bold** text
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><blockquote>This is a quote with multiple lines and <b>bold</b> text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- First item with **bold**
- Second item with `code`
- Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><ul><li>First item with <b>bold</b></li><li>Second item with <code>code</code></li><li>Third item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. First item
2. Second item with _italic_
3. Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><ol><li>First item</li><li>Second item with <i>italic</i></li><li>Third item</li></ol></div>",
        )

    def test_mixed_blocks(self):
        md = """
# Heading

This is a paragraph.

- List item 1
- List item 2

> A quote
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><h1>Heading</h1><p>This is a paragraph.</p><ul><li>List item 1</li><li>List item 2</li></ul><blockquote>A quote</blockquote></div>",
        )

if __name__ == "__main__":
    unittest.main()