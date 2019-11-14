import json
import os

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
tree_pic_path = os.path.join(base_path, "treePic")
data_path = os.path.join(base_path, "data")
query_output_path = os.path.join(base_path, "queryOutput")
index_path = os.path.join(base_path, "index")


def _get_content(path, page_name):
    with open(os.path.join(path, page_name), "r") as f:
        content = json.load(f)
        return content


def _append_to_page(path, page_name, content):
    with open(os.path.join(path, page_name), "a") as f:
        f.write(content)


def read_tree(display_file_name, fname, table_num):
    content = _get_content(index_path, fname)
    table_space = ""
    for x in range(0, table_num):
        table_space += "  "
    _append_to_page(tree_pic_path, display_file_name, table_space + fname + ":" + json.dumps(content) + '\r\n')
    if content[0] != 'L':
        data_sets = content[2]
        for idx, value in enumerate(data_sets):
            if idx % 2 == 0:
                read_tree(display_file_name, value, table_num + 2)


def displayTree(fname):
    b_tree_schema = _get_content(index_path, 'directory.txt')
    display_file_name = None
    for row in b_tree_schema:
        if fname in row:
            display_file_name = row[0] + '_' + row[1] + '.txt'
            break
    if display_file_name is not None:
        read_tree(display_file_name, fname, 0)
    return display_file_name


def displayTable(rel, fname):
    _append_to_page(query_output_path, fname, 'Result Table' + '\r\n')

    cols = [row for row in _get_content(data_path, 'schemas.txt') if row[0] == rel]
    cols.sort(key=lambda r: r[3])

    rel_path = os.path.join(data_path, rel)

    rows = []
    for page_name in _get_content(rel_path, 'pageLink.txt'):
        rows += _get_content(rel_path, page_name)

    max_len = [len(col[1]) for col in cols]

    for row in rows:
        for i, s in enumerate(row):
            max_len[i] = max(max_len[i], len(str(s)))

    separator = '+'
    for l in max_len:
        separator += '-' * (l + 2) + '+'

    separator += '\r\n'

    def _generate_row(row):
        output = '|'

        for i, elem in enumerate(row):
            s = str(elem)
            if len(s) < max_len[i]:
                s += ' ' * (max_len[i] - len(s))

            output += ' ' + s + ' |'

        return output + '\r\n'

    result = separator + _generate_row([col[1] for col in cols]) + separator

    for row in rows:
        result += _generate_row(row)

    result += separator

    _append_to_page(query_output_path, fname, result)
