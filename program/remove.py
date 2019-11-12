import json
import os
import shutil


base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
data_path = os.path.join(base_path, "data")
index_path = os.path.join(base_path, "index")


def _do_remove_tree(page_name, page_list):
    page_path = os.path.join(index_path, page_name)

    page = json.load(open(page_path, "r"))
    if page[0] == "I":
        for i in range(0, len(page[2]), 2):
            _do_remove_tree(page[2][i], page_list)

    page_list.append(page_name)
    os.unlink(page_path)


def removeTree(rel, att):
    directory_path = os.path.join(index_path, "directory.txt")

    page_list = []

    directory = json.load(open(directory_path, "r"))
    for i, root in enumerate(directory):
        if root[0] == rel and root[1] == att:
            _do_remove_tree(root[2], page_list)
            directory = directory[:i] + directory[i + 1:]
            json.dump(directory, open(directory_path, "w"))
            break

    page_pool_path = os.path.join(index_path, "pagePool.txt")
    page_pool = json.load(open(page_pool_path, "r"))
    page_pool += page_list

    json.dump(page_pool, open(page_pool_path, "w"))


def removeTable(rel):
    schema_path = os.path.join(data_path, "schemas.txt")

    schema = json.load(open(schema_path, "r"))
    schema = [s for s in schema if s[0] != rel]
    json.dump(schema, open(schema_path, "w"))

    page_pool_path = os.path.join(data_path, "pagePool.txt")
    page_pool = json.load(open(page_pool_path))

    rel_path = os.path.join(data_path, rel)
    for page in json.load(open(os.path.join(rel_path, "pageLink.txt"), "r")):
        page_pool.append(page)

    json.dump(page_pool, open(page_pool_path, "w"))

    shutil.rmtree(rel_path)

