import json
import os

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
tree_pic_path = os.path.join(base_path, "treePic")
index_path = os.path.join(base_path, "index")


def _get_content(page_name):
    with open(os.path.join(index_path, page_name), "r") as f:
        content = json.load(f)
        return content


def _append_to_page(page_name, content):
    with open(os.path.join(tree_pic_path, page_name), "a") as f:
        f.write(content)


def read_tree(display_file_name, fname, table_num):
    content = _get_content(fname)
    table_space = ""
    for x in range(0, table_num):
        table_space += "  "
    _append_to_page(display_file_name, table_space + fname + ":" + json.dumps(content) + '\r\n')
    if content[0] != 'L':
        data_sets = content[2]
        for idx, value in enumerate(data_sets):
            if idx % 2 == 0:
                read_tree(display_file_name, value, table_num + 2)


def displayTree(fname):
    b_tree_schema = _get_content('directory.txt')
    display_file_name = None
    for row in b_tree_schema:
        if fname in row:
            display_file_name = row[0] + '_' + row[1] + '.txt'
            break
    if display_file_name is not None:
        read_tree(display_file_name, fname, 0)
    return display_file_name


def displayTable(rel, fname):
    pass

