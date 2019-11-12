#!C:\Users\LSS\AppData\Local\Programs\Python\Python37\python.exe
from buildTree import build
from display import displayTree

root = build('Suppliers', 'sid', 2)
page_name = displayTree(root)
print(root + ":" + page_name)
root = build('Supply', 'pid', 2)
page_name = displayTree(root)
print(root + ":" + page_name)