from enum import Enum
from htmlnode import ParentNode, text_node_to_html_node
from textnode import TextNode, TextType, text_to_textnodes

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    DEFAULT = "default"  # keep for tests


def markdown_to_blocks(markdown):
    lines = markdown.splitlines()
    blocks = []
    cur = []
    in_code = False
    for line in lines:
        if line.strip() == "```":
            if not in_code:
                # starting a fence: flush current block, start code block
                if cur:
                    blocks.append("\n".join(cur).strip())
                    cur = []
                cur = ["```"]
                in_code = True
            else:
                # closing fence: finish code block
                cur.append("```")
                blocks.append("\n".join(cur).strip())
                cur = []
                in_code = False
            continue
        if in_code:
            cur.append(line)
            continue
        if line.strip() == "":
            if cur:
                blocks.append("\n".join(cur).strip())
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur).strip())
    return [b for b in blocks if b]

def block_to_block_type(block):
    lines = block.split("\n")

    # code
    if len(lines) >= 2 and lines[0].strip() == "```" and lines[-1].strip() == "```":
        return BlockType.CODE

    # heading: only first line, 1–6 hashes followed by a space
    first = lines[0]
    i = 0
    while i < len(first) and first[i] == "#":
        i += 1
    if 1 <= i <= 6 and i < len(first) and first[i] == " ":
        return BlockType.HEADING

    # quote: every line starts with ">"
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # unordered: every line starts with "- "
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # ordered: lines are "1. ...", "2. ...", ... exactly
    ok = True
    for idx, line in enumerate(lines, start=1):
        # find first "."
        dot = line.find(".")
        if dot == -1:
            ok = False
            break
        num_str = line[:dot]
        if not num_str.isdigit():
            ok = False
            break
        if int(num_str) != idx:
            ok = False
            break
        if dot + 1 >= len(line) or line[dot + 1] != " ":
            ok = False
            break
    if ok:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    children = []
    blocks_result = markdown_to_blocks(markdown)
    for block in blocks_result:
        bt = block_to_block_type(block)
        first = block.split("\n")[0] if block else ""
        last = block.split("\n")[-1] if block else ""
        print("BlockType:", bt, "| first:", repr(first), "| last:", repr(last))
        match bt:
            case BlockType.CODE:
                lines = block.split("\n")
                # strip the first and last fence lines
                inner = "\n".join(lines[1:-1])
                text_node = TextNode(inner, TextType.TEXT)
                code_node = ParentNode("code", [text_node_to_html_node(text_node)])
                pre_node = ParentNode("pre", [code_node])
                children.append(pre_node)
            case BlockType.HEADING:
                heading_count = len(block)-len(block.lstrip('#'))
                heading_content = block[heading_count:].strip()
                
                  # Parse inline markdown (like paragraphs!)
                node_result = text_to_textnodes(heading_content)
                html_nodes = []
                for text_node in node_result:
                    html_node = text_node_to_html_node(text_node)
                    html_nodes.append(html_node)

                heading_node = ParentNode(f"h{heading_count}", html_nodes) 
                children.append(heading_node)
            case BlockType.QUOTE:
                # Split into lines, strip '> ' from each, then rejoin
                lines = block.split('\n')
                quote_lines = [line.lstrip('> ').strip() for line in lines]
                quote_content = ' '.join(quote_lines)
    
                # Parse inline markdown
                node_result = text_to_textnodes(quote_content)
                html_nodes = []
                for text_node in node_result:
                    html_node = text_node_to_html_node(text_node)
                    html_nodes.append(html_node)
    
                quote_node = ParentNode("blockquote", html_nodes)
                children.append(quote_node)
            case BlockType.UNORDERED_LIST:
                # Split into individual lines (each is a list item)
                lines = block.split('\n')
    
                list_items = []
                for line in lines:
                    item_text = line.lstrip('*- ').strip()
                    print("UL item:", repr(item_text))  # add this
                    node_result = text_to_textnodes(item_text)
                    html_nodes = []
                    for text_node in node_result:
                        html_node = text_node_to_html_node(text_node)
                        html_nodes.append(html_node)
        
                    # Create <li> node for this item
                    li_node = ParentNode("li", html_nodes)
                    list_items.append(li_node)
    
                # Wrap all <li> nodes in <ul>
                ul_node = ParentNode("ul", list_items)
                children.append(ul_node)
            case BlockType.ORDERED_LIST:
                lines = block.split('\n')
                list_items = []
                for line in lines:
                    dot = line.find(". ")
                    item_text = line[dot+2:] if dot != -1 else line  # precise cut
                    print("OL item:", repr(item_text))  # add this
                    node_result = text_to_textnodes(item_text)
                    html_nodes = []
                    for text_node in node_result:
                        html_node = text_node_to_html_node(text_node)
                        html_nodes.append(html_node)
                    li_node = ParentNode("li", html_nodes)
                    list_items.append(li_node)
                ul_node = ParentNode("ol", list_items)
                children.append(ul_node)
            case BlockType.PARAGRAPH:
                # Replace newlines with spaces within the paragraph
                paragraph_text = block.replace('\n', ' ')
    
                node_result = text_to_textnodes(paragraph_text)
                html_nodes = []
                for text_node in node_result:
                    html_node = text_node_to_html_node(text_node)
                    html_nodes.append(html_node)
                children.append(ParentNode('p', html_nodes))
    return ParentNode('div', children)



