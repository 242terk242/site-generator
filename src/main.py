import shutil,os, sys
from markdown_blocks import markdown_to_html_node

path_public = './public'
path_static = './static'
path_docs = './docs'

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

def generate_page(from_path, template_path, dest_path, basepath="/"):
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
    update_href = uodate_html.replace('href="/', f'href="{basepath}')
    update_src = update_href.replace('src="/', f'src="{basepath}')
    with open(dest_path, "w") as file:
        file.write(update_src)

def main():

    basepath = "/"
    if sys.argv[1:]:
        print(f"{sys.argv}")
        basepath = sys.argv[1]
        print("------------------------------------------------")
        print(f"User prompt: {basepath}")


    if os.path.exists(path_docs):
        shutil.rmtree(path_docs)
    os.mkdir(path_docs, mode=0o777, dir_fd=None)
    copy_recursive(path_static, path_docs)
    for dirpath, dirnames, filenames in os.walk("./content"):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            src_md = os.path.join(dirpath, name)
            rel = os.path.relpath(src_md, "content")
            out_dir = os.path.join("docs", os.path.dirname(rel))  
            os.makedirs(out_dir, exist_ok=True)
            base = os.path.basename(src_md)
            if base == "index.md":
                out_html = os.path.join(out_dir, "index.html")
            else:
                out_html = os.path.join(out_dir, os.path.splitext(base)[0] + ".html")
            generate_page(src_md, "./template.html", out_html, basepath)

main()