from enum import Enum
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"
    DEFAULT = "default"  # keep for tests

class TextNode():

    def __init__(self, text="", text_type = None, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url)
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        text = node.text
        if delimiter not in text:
            new_nodes.append(node)
            continue
        parts = text.split(delimiter)
        # unmatched delimiter → fall back to plain text
        if len(parts) % 2 == 0:
            new_nodes.append(TextNode(text, TextType.TEXT))
            continue
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                if part:
                    new_nodes.append(TextNode(part, text_type))
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(links):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", links)

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        remaining = node.text
        while True:
            matches = extract_markdown_images(remaining)
            if not matches:
                if remaining:
                    new_nodes.append(TextNode(remaining, TextType.TEXT))
                break

            alt, url = matches[0]
            before, after = remaining.split(f"![{alt}]({url})", 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            remaining = after
    return new_nodes

def split_nodes_links(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        remaining = node.text
        while True:
            matches = extract_markdown_links(remaining)
            if not matches:
                if remaining:
                    new_nodes.append(TextNode(remaining, TextType.TEXT))
                break

            alt, url = matches[0]
            before, after = remaining.split(f"[{alt}]({url})", 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.LINK, url))
            remaining = after
    return new_nodes

def text_to_textnodes(text):
    start_list = [TextNode(text, TextType.TEXT)]
    split_image = split_nodes_image(start_list)
    split_links = split_nodes_links(split_image)
    split_code = split_nodes_delimiter(split_links, "`", TextType.CODE)
    split_bold = split_nodes_delimiter(split_code, "**", TextType.BOLD)
    split_line = split_nodes_delimiter(split_bold, "_", TextType.ITALIC)
    return split_line
