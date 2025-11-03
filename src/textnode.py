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
    node_list = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            node_list.append(node)
        else:
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0: 
                raise Exception("invalid markdown syntax")
            if len(parts) == 1:
                node_list.append(node)
            else: 
                for i, part in enumerate(parts):
                    if part == "": 
                        continue
                    if i % 2 == 0: 
                        node_list.append(TextNode(part,TextType.TEXT))
                    else: 
                        node_list.append(TextNode(part, text_type))
    return node_list

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