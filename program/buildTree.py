import json
import os

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
data_path = os.path.join(base_path, "data")
index_path = os.path.join(base_path, "index")


def _get_index_of_att(rel, att):
    with open(os.path.join(data_path, "schemas.txt"), "r") as f:
        schemas = json.load(f)
    columns = [{
        "name": col[1],
        "type": col[2],
        "index": col[3]
    } for col in schemas if col[0] == rel]
    search_column = [col for col in columns if col["name"] == att][0]
    att_index = search_column["index"]
    return att_index


def _write_new_page(content):
    page_pool = "pagePool.txt"
    with open(os.path.join(index_path, page_pool), "r") as f:
        pages = json.load(f)
        page_name = pages.pop()

    with open(os.path.join(index_path, page_pool), "w") as f:
        json.dump(pages, f)

    with open(os.path.join(index_path, page_name), "w") as page_file:
        json.dump(content, page_file)
    return page_name


def _get_content(page_name):
    with open(os.path.join(index_path, page_name), "r") as f:
        content = json.load(f)
        return content


def _write_to_page(page_name, content):
    with open(os.path.join(index_path, page_name), "w") as f:
        json.dump(content, f)


def _find_leaf(parent, key):
    read_content = _get_content(parent)
    if read_content[0] == 'L':
        leaf_page = parent
    else:
        internal_content = read_content[2]
        index = -1
        for idx, val in enumerate(internal_content):
            if idx % 2 != 0:
                if key < val:
                    index = idx
                    break
        if index == -1:
            index = len(internal_content)
        node_page = internal_content[index - 1]
        leaf_page = _find_leaf(node_page, key)
    return leaf_page


def _insert_page_into_node(left_page, right_page, max_element, root):
    left_content = _get_content(left_page)
    right_content = _get_content(right_page)
    node_type = left_content[0]
    parent = left_content[1]
    if node_type == 'L':
        middle_value = right_content[4][0]
    else:
        middle_value = right_content[2][1]
        right_content[2] = right_content[2][2:]
        _write_to_page(right_page, right_content)
    if parent == 'nil':
        parent_content = ['I', 'nil', []]
        parent_content[2].append(left_page)
        parent_content[2].append(middle_value)
        parent_content[2].append(right_page)
        root = _write_new_page(parent_content)
        left_content[1] = root
        right_content[1] = root
        _write_to_page(left_page, left_content)
        _write_to_page(right_page, right_content)
        return root
    else:
        parent_content = _get_content(parent)
        parent_sets = parent_content[2]
        insert_index = parent_sets.index(left_page)
        parent_sets.insert(insert_index + 1, right_page)
        parent_sets.insert(insert_index + 1, middle_value)
        if len(parent_sets) > (2 * max_element + 1):
            # split parent_sets
            split_index = max_element + 1
            left_list = parent_sets[:split_index]
            right_list = parent_sets[split_index - 1:]
            parent_content[2] = left_list
            _write_to_page(parent, parent_content)
            new_right_content = ['I', 'nil', right_list]
            new_page_name = _write_new_page(new_right_content)
            for idx, item in enumerate(right_list[2:]):
                if idx % 2 == 0:
                    temp_name = item
                    temp_content = _get_content(temp_name)
                    temp_content[1] = new_page_name
                    _write_to_page(temp_name, temp_content)
            return _insert_page_into_node(parent, new_page_name, max_element, root)
        else:
            right_content[1] = parent
            _write_to_page(right_page, right_content)
            _write_to_page(parent, parent_content)
            return root


def _insert_into_leaf(left_list, data_set):
    key = data_set[0]
    index = -1
    for idx, val in enumerate(left_list):
        if idx % 2 == 0:
            if key < val:
                index = idx
                break
    if index == -1:
        left_list += data_set
    else:
        left_list.insert(index, data_set[1])
        left_list.insert(index, data_set[0])
    return left_list


def _insert_key(root, data_set, max_element):
    if root is None:
        content = ['L', 'nil', 'nil', 'nil', []]
        content[4] += data_set
        root = _write_new_page(content)
    else:
        key = data_set[0]
        leaf_page = _find_leaf(root, key)
        leaf_content = _get_content(leaf_page)
        read_data_sets = leaf_content[4]
        if len(read_data_sets) >= (2 * max_element):
            # overflow happens
            if key in read_data_sets:
                # check if key already exists
                rid_list = read_data_sets[read_data_sets.index(key) + 1]
                rid_list += (data_set[1])
                _write_to_page(leaf_page, leaf_content)
            else:
                # key did not exist, split
                result = _insert_into_leaf(read_data_sets, data_set)
                # original leaf sets overflow, split it into two lists
                split_index = int(len(result) / 2 - 1)
                left_list = result[:split_index]
                right_list = result[split_index:]
                linked_right_leaf_name = leaf_content[3]
                new_leaf_content = ['L', 'nil', leaf_page, linked_right_leaf_name, right_list]
                new_page_name = _write_new_page(new_leaf_content)
                if linked_right_leaf_name != 'nil':
                    linked_right_leaf_content = _get_content(linked_right_leaf_name)
                    linked_right_leaf_content[2] = new_page_name
                    _write_to_page(linked_right_leaf_name, linked_right_leaf_content)
                leaf_content[3] = new_page_name
                leaf_content[4] = left_list
                _write_to_page(leaf_page, leaf_content)
                root = _insert_page_into_node(leaf_page, leaf_content[3], max_element, root)
        else:
            if key in read_data_sets:
                # check if key already exists
                rid_list = read_data_sets[read_data_sets.index(key) + 1]
                rid_list += (data_set[1])
                _write_to_page(leaf_page, leaf_content)
            else:
                # insert data set into leaf page
                leaf_content[4] = _insert_into_leaf(read_data_sets, data_set)
                _write_to_page(leaf_page, leaf_content)
    return root


def build(rel, att, od):
    max_element = 2 * od
    index_att = _get_index_of_att(rel, att)
    # root of B+ tree
    root = None
    # read data records to extract search keys
    rel_path = os.path.join(data_path, rel)
    page_link = json.load(open(os.path.join(rel_path, "pageLink.txt"), "r"))
    for page_name in page_link:
        page = json.load(open(os.path.join(rel_path, page_name), "r"))
        for idx, row in enumerate(page):
            # create data_set for search key
            data_set = []
            data_rids = [page_name + "." + str(idx)]
            data_set.append(row[index_att])
            data_set.append(data_rids)
            # insert search key into B+ tree
            root = _insert_key(root, data_set, max_element)

    return root
