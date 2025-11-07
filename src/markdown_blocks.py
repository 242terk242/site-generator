from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    DEFAULT = "default"  # keep for tests


def markdown_to_blocks(markdown):
    split_result = markdown.split("\n\n")
    for i in range(0, len(split_result)):
        split_result[i] = split_result[i].strip()
    filtered_list = [s for s in split_result if s.strip()]
    return filtered_list

def block_to_block_type(block):
    lines = block.split("\n")

    # code
    if len(lines) >= 2 and lines[0] == "```" and lines[-1] == "```":
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