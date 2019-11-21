import json
import os
import binascii

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
data_path = os.path.join(base_path, "data")
index_path = os.path.join(base_path, "index")
op_lambdas = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}


def _read_schemas():
    with open(os.path.join(data_path, "schemas.txt"), "r") as f:
        return json.load(f)


def _get_cols(rel):
    schemas = _read_schemas()

    columns = [{
        "name": col[1],
        "type": col[2],
        "index": col[3]
    } for col in schemas if col[0] == rel]

    return columns


def _write_relation_page(rel, page):
    page_pool_path = os.path.join(data_path, "pagePool.txt")
    page_pool = json.load(open(page_pool_path, "r"))

    page_name = page_pool.pop()

    json.dump(page_pool, open(page_pool_path, "w"))

    rel_path = os.path.join(data_path, rel)

    json.dump(page, open(os.path.join(rel_path, page_name), "w"))

    page_link_path = os.path.join(rel_path, 'pageLink.txt')
    if os.path.exists(page_link_path):
        json.dump(json.load(open(page_link_path, "r")) + [page_name], open(page_link_path, "w"))
    else:
        json.dump([page_name], open(page_link_path, "w"))


def _write_result(cols, rows):
    while True:
        rel = "Temp_" + binascii.b2a_hex(os.urandom(15)).decode('ascii')
        path = os.path.join(data_path, rel)
        if not os.path.isdir(path):
            os.mkdir(path)
            break

    page = []

    for row in rows:
        page.append(row)

        if len(page) == 2:
            _write_relation_page(rel, page)
            page = []

    if len(page) > 0:
        _write_relation_page(rel, page)

    schemas = _read_schemas() + list(map(lambda col: [rel] + list(col.values()), cols))

    with open(os.path.join(data_path, "schemas.txt"), "w") as f:
        json.dump(schemas, f)

    return rel


def _scan_table(callback, rel):
    rel_path = os.path.join(data_path, rel)
    page_link = json.load(open(os.path.join(rel_path, "pageLink.txt"), "r"))
    cost = 0

    for page_name in page_link:
        page = json.load(open(os.path.join(rel_path, page_name), "r"))
        cost += 1
        for row in page:
            callback(row)
    return cost


def _scan_b_tree(root, op, val):
    cost = 0
    content = json.load(open(os.path.join(index_path, root), "r"))
    cost += 1
    if content[0] != 'L':
        compare_list = content[2]
        index = -1
        for idx, value in enumerate(compare_list):
            if idx % 2 != 0 and val < value:
                index = idx
                break
        if index == -1:
            index = len(compare_list)
        new_root = compare_list[index - 1]
        new_scan_result = _scan_b_tree(new_root, op, val)
        cost += new_scan_result[0]
        return [cost, new_scan_result[1]]
    else:
        data_sets = content[4]
        result_list = []
        for idx, value in enumerate(data_sets):
            if idx % 2 == 0 and op_lambdas[op](value, val):
                result_list += data_sets[idx + 1]
        if '<' in op:
            new_result = _scan_all_leaf_nodes_from('L', content[2])
            result_list += new_result[1]
            cost += new_result[0]
        elif '>' in op:
            new_result = _scan_all_leaf_nodes_from('R', content[3])
            result_list += new_result[1]
            cost += new_result[0]
        return [cost, result_list]


def _get_tuples(rel, rid_list):
    result = []
    rel_path = os.path.join(data_path, rel)
    for row in rid_list:
        offset = int(row[-1:])
        page_name = row[:-2]
        content = json.load(open(os.path.join(rel_path, page_name), "r"))
        result.append(content[offset])
    return result


def _scan_all_leaf_nodes_from(direction, start_page):
    result = []
    cost = 0
    if start_page == 'nil':
        return [cost, result]
    content = json.load(open(os.path.join(index_path, start_page), "r"))
    cost += 1
    data_sets = content[4]
    for idx, value in enumerate(data_sets):
        if idx % 2 != 0:
            result += value
    if direction == 'L':
        new_start_page = content[2]
    else:
        new_start_page = content[3]
    new_result = _scan_all_leaf_nodes_from(direction, new_start_page)
    cost += new_result[0]
    result += new_result[1]
    return [cost, result]


def select(rel, att, op, val):
    columns = _get_cols(rel)

    search_column = [col for col in columns if col["name"] == att][0]

    index = None
    for root in json.load(open(os.path.join(index_path, "directory.txt"), "r")):
        if root[0] == rel and root[1] == att:
            # index = json.load(open(os.path.join(index_path, root[2]), "r"))
            index = root[2]
            break

    results = []

    if index is not None:
        tree_result = _scan_b_tree(index, op, val)
        cost = tree_result[0]
        result_tuples = _get_tuples(rel, tree_result[1])
        results += result_tuples
        cost += len(tree_result[1])
        output_str = 'With B+_tree, the cost of searching '\
                     + att + ' ' + op + ' ' + str(val) + ' on ' + rel + ' is ' + str(cost) + ' pages'
    else:
        def _scan_callback(row):
            if op_lambdas[op](row[search_column["index"]], val):
                results.append(row)

        cost = _scan_table(_scan_callback, rel)
        output_str = 'Without B+_tree, the cost of searching '\
                     + att + ' ' + op + ' ' + str(val) + ' on ' + rel + ' is ' + str(cost) + ' pages'
    print(output_str)

    return _write_result(columns, results)


def project(rel, attr_list):
    columns = [col for col in _get_cols(rel) if col["name"] in attr_list]

    col2index = {}
    for col in columns:
        col2index[col["name"]] = col["index"]

    results = []

    def _scan_callback(row):
        result = []
        for col in attr_list:
            result.append(row[col2index[col]])

        result = tuple(result)
        if result not in results:
            results.append(result)

    _scan_table(_scan_callback, rel)

    for col in columns:
        col["index"] = attr_list.index(col["name"])

    return _write_result(columns, results)


def join(rel1, att1, rel2, att2):
    c1 = _get_cols(rel1)
    c2 = _get_cols(rel2)

    i1 = [col for col in c1 if col["name"] == att1][0]["index"]
    i2 = [col for col in c2 if col["name"] == att2][0]["index"]

    results = []

    rel_with_b_tree = None
    rel_root = None
    external_rel = None
    index_external = None
    index_internal = None
    column_external = None
    column_internal = None
    for root in json.load(open(os.path.join(index_path, "directory.txt"), "r")):
        if root[0] == rel1 and root[1] == att1:
            # index = json.load(open(os.path.join(index_path, root[2]), "r"))
            rel_with_b_tree = rel1
            rel_root = root[2]
            external_rel = rel2
            index_external = i2
            index_internal = i1
            column_external = c2
            column_internal = c1
            break
        if root[0] == rel2 and root[1] == att2:
            rel_with_b_tree = rel2
            rel_root = root[2]
            external_rel = rel1
            index_external = i1
            index_internal = i2
            column_external = c1
            column_internal = c2
            break

    if rel_with_b_tree is not None:
        cost = 0
        external_page_names = json.load(open(os.path.join(data_path, external_rel, "pageLink.txt"), "r"))
        for page_name in external_page_names:
            external_page_content = json.load(open(os.path.join(data_path, external_rel, page_name), "r"))
            cost += 1
            for tuple in external_page_content:
                key = tuple[index_external]
                scan_result = _scan_b_tree(rel_root, '=', key)
                cost += scan_result[0]
                equivalent_internal_tuples = _get_tuples(rel_with_b_tree, scan_result[1])
                cost += len(scan_result[1])
                for equivalent_tuple in equivalent_internal_tuples:
                    results.append(tuple + equivalent_tuple[:index_internal] + equivalent_tuple[index_internal + 1:])
        # output_str = 'With B+_tree, the cost of joining '\
        #             + rel1 + ', ' + rel2 + ' on ' + att1 + ', ' + att2 + ' is ' + str(cost) + ' pages'
        # print(output_str)
        columns = column_external + column_internal[:index_internal] + column_internal[index_internal + 1:]

        i = 0
        for col in columns:
            col["index"] = i
            i = i + 1
    else:
        pl1 = json.load(open(os.path.join(data_path, rel1, "pageLink.txt"), "r"))
        pl2 = json.load(open(os.path.join(data_path, rel2, "pageLink.txt"), "r"))

        for pname1 in pl1:
            p1 = json.load(open(os.path.join(data_path, rel1, pname1), "r"))
            for pname2 in pl2:
                p2 = json.load(open(os.path.join(data_path, rel2, pname2), "r"))
                for r1 in p1:
                    for r2 in p2:
                        if r1[i1] == r2[i2]:
                            results.append(r1 + r2[:i2] + r2[i2 + 1:])

        columns = c1 + c2[:i2] + c2[i2 + 1:]

        i = 0
        for col in columns:
            col["index"] = i
            i = i + 1
    return _write_result(columns, results)
