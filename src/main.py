import shutil,os
from markdown_blocks import markdown_to_html_node

path_public = './public'
path_static = './static'

def copy_recursive(src, dst):
    contents = os.listdir(src)
    for content in contents:
        if os.path.isfile(src + "/" + content):
            shutil.copy(src + "/" + content, dst)
        else:
            os.makedirs(dst + "/" + content, exist_ok=True)
            copy_recursive(src + "/" + content, dst + "/" + content)

def extract_title(markdown):
    split_result = markdown.split("\n\n")
    heading_count = len(split_result[0])-len(split_result[0].lstrip('#'))
    heading_content = ""
    if heading_count == 0:
        raise Exception("No header in markdown")
    else:
        heading_content = split_result[0][heading_count:].strip()
    return heading_content

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown_result = ""
    template_result = ""
    with open(from_path) as f:
        markdown_result = f.read()
    with open(template_path) as f:
        template_result = f.read()
    print("Parsing:", from_path)
    markdown_html = markdown_to_html_node(markdown_result).to_html()
    title = extract_title(markdown_result)
    uodate_title = template_result.replace("{{ Title }}", title)
    uodate_html = uodate_title.replace("{{ Content }}", markdown_html)
    with open(dest_path, "w") as file:
        file.write(uodate_html)

def main():
    if os.path.exists(path_public):
        shutil.rmtree(path_public)
    os.mkdir(path_public, mode=0o777, dir_fd=None)
    copy_recursive(path_static, path_public)
    for dirpath, dirnames, filenames in os.walk("./content"):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            src_md = os.path.join(dirpath, name)             # full source file
            rel = os.path.relpath(src_md, "content")         # e.g., blog/glorfindel/index.md
            out_dir = os.path.join("public", os.path.dirname(rel))  # public/blog/glorfindel
            os.makedirs(out_dir, exist_ok=True)
            base = os.path.basename(src_md)
            if base == "index.md":
                out_html = os.path.join(out_dir, "index.html")
            else:
                out_html = os.path.join(out_dir, os.path.splitext(base)[0] + ".html")
            generate_page(src_md, "./template.html", out_html)

main()