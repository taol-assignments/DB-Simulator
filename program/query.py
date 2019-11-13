#!C:\Users\LSS\AppData\Local\Programs\Python\Python37\python.exe
from buildTree import build
from display import displayTree
from display import displayTable
from remove import removeTree
from remove import removeTable
from relAlg import select
from relAlg import join

root = build('Suppliers', 'sid', 2)
page_name = displayTree(root)
print(root + ":" + page_name)
root = build('Supply', 'pid', 2)
page_name = displayTree(root)
print(root + ":" + page_name)

# print(select('Supply', 'sid', '>', "s18"))
print(join('Supply', 'pid', 'Products', 'pid'))
# removeTable('Temp_19c11df38f6e6a95dec8d743bb3efa')
# removeTree('Suppliers', 'sid')

