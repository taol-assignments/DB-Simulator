import json


def select(rel, att, op, val):
    page_link = json.load(open("data/" + rel + "/pageLink.txt", "r"))
