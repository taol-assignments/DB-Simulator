import json
import os
import binascii

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
data_path = os.path.join(base_path, "data")


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
    with open(os.path.join(data_path, "pagePool.txt"), "r") as f:
        page_pool = json.load(f)
        page_name = page_pool.pop()

    with open(os.path.join(data_path, "pagePool.txt"), "w") as f:
        json.dump(page_pool, f)

        with open(os.path.join(data_path, rel, page_name), "w") as page_file:
            json.dump(page, page_file)


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

    for page_name in page_link:
        page = json.load(open(os.path.join(rel_path, page_name), "r"))
        for row in page:
            callback(row)


def select(rel, att, op, val):
    columns = _get_cols(rel)

    search_column = [col for col in columns if col["name"] == att][0]

    op_lambdas = {
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        "=": lambda a, b: a == b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }

    index = None
    index_path = os.path.join(base_path, "index")
    for root in json.load(open(os.path.join(index_path, "directory.txt"), "r")):
        if root[0] == rel and root[1] == att:
            index = json.load(open(os.path.join(index_path, root[2]), "r"))
            break

    results = []

    if index:
        pass
    else:
        def _scan_callback(row):
            if op_lambdas[op](row[search_column["index"]], val):
                results.append(row)

        _scan_table(_scan_callback, rel)

    return _write_result(columns, results)


def project(rel, *attr_list):
    attr_list = list(attr_list)

    columns = [col for col in _get_cols(rel) if col["name"] in attr_list]

    i = 0
    for col in columns:
        col["index"] = i
        i += 1

    results = []

    def _scan_callback(row):
        result = []
        for col in columns:
            result.append(row[col["index"]])

        result = tuple(result)
        if result not in results:
            results.append(result)

    _scan_table(_scan_callback, rel)

    return _write_result(columns, results)


def join(rel1, att1, rel2, att2):
    c1 = _get_cols(rel1)
    c2 = _get_cols(rel2)

    i1 = [col for col in c1 if col["name"] == att1][0]["index"]
    i2 = [col for col in c2 if col["name"] == att2][0]["index"]

    results = []

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
