#!C:\Users\LSS\AppData\Local\Programs\Python\Python37\python.exe
from buildTree import build
from display import displayTree, displayTable
from remove import removeTree, removeTable
from relAlg import select, project, join
import os


base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
query_output_path = os.path.join(base_path, "queryOutput")
query_result_page = 'queryResult.txt'


# build B+ Tree on Suppliers.sid and Supply.pid, then display them under treePic
displayTree(build('Suppliers', 'sid', 2))
displayTree(build('Supply', 'pid', 2))


# a. Find the name for the supplier ‘s23’ when a B+_tree exists on Suppliers.sid.
# Find the name for the supplier ‘s23’ using the B+_tree
temp_relation_after_selection = select('Suppliers', 'sid', '=', 's23')
result_relation_after_projection = project(temp_relation_after_selection, ['sname'])
# remove the temp relation table
removeTable(temp_relation_after_selection)
# display the result relation under folder queryOutput with name: queryResult.txt
open(os.path.join(query_output_path, query_result_page), "a").write(
    "a. Find the name for the supplier 's23' when a B+_tree exists on Suppliers.sid.\n")
displayTable(result_relation_after_projection, query_result_page)
# remove the result relation table
removeTable(result_relation_after_projection)


# b. Remove the B+_tree from Suppliers.sid, and repeat Question a.
# remove B+ tree on suppliers
removeTree('Suppliers', 'sid')
# Find the name for the supplier ‘s23’ without a B+ tree
temp_relation_after_selection = select('Suppliers', 'sid', '=', 's23')
# project temp relation on the attribute 'sname'
result_relation_after_projection = project(temp_relation_after_selection, ['sname'])
# remove the temp relation table
removeTable(temp_relation_after_selection)
# display the result relation under folder queryOutput with name: queryResult.txt
open(os.path.join(query_output_path, query_result_page), "a").write(
    "b. Remove the B+_tree from Suppliers.sid, and repeat Question a.\n")
displayTable(result_relation_after_projection, query_result_page)
# remove the result relation table
removeTable(result_relation_after_projection)


# c. Find the address of the suppliers who supplied 'p15'.
# join the two relation 'Suppliers' and 'Supply' on 'sid'
temp_relation_after_join = join('Suppliers', 'sid', 'Supply', 'sid')
# select from the temp relation where 'pid' = 'p15'
temp_relation_after_selection = select(temp_relation_after_join, 'pid', '=', 'p15')
removeTable(temp_relation_after_join)
# project result relation on the attribute 'address'
result_relation_after_projection = project(temp_relation_after_selection, ['address'])
removeTable(temp_relation_after_selection)
# display the result relation under folder queryOutput with name: queryResult.txt
open(os.path.join(query_output_path, query_result_page), "a").write(
    "c. Find the address of the suppliers who supplied 'p15'.\n")
displayTable(result_relation_after_projection, query_result_page)
removeTable(result_relation_after_projection)


# d. What is the cost of 'p20' supplied by 'Kiddie'?
# join the two relation 'Suppliers' and 'Supply' on 'sid'
temp_relation_after_join = join('Suppliers', 'sid', 'Supply', 'sid')
# select from the temp relation where 'sname = 'Kiddie'
temp_relation_after_selection1 = select(temp_relation_after_join, 'sname', '=', 'Kiddie')
removeTable(temp_relation_after_join)
# select from the temp relation where 'pid = 'p20'
temp_relation_after_selection2 = select(temp_relation_after_selection1, 'pid', '=', 'p20')
removeTable(temp_relation_after_selection1)
# project result relation on the attribute 'cost'
result_relation_after_projection = project(temp_relation_after_selection2, ['cost'])
removeTable(temp_relation_after_selection2)
# display the result relation under folder queryOutput with name: queryResult.txt
open(os.path.join(query_output_path, query_result_page), "a").write(
    "d. What is the cost of 'p20' supplied by 'Kiddie'?\n")
displayTable(result_relation_after_projection, query_result_page)
removeTable(result_relation_after_projection)


# e. For each supplier who supplied products with a cost of 47 or higher, list his/her name, product name and the cost.
# join the two relation 'Suppliers' and 'Supply' on 'sid'
temp_relation_after_join1 = join('Suppliers', 'sid', 'Supply', 'sid')
# join the result relation with Products on 'pid'
temp_relation_after_join2 = join(temp_relation_after_join1, 'pid', 'Products', 'pid')
removeTable(temp_relation_after_join1)
# select from the temp relation where 'cost >= 47'
temp_relation_after_selection = select(temp_relation_after_join2, 'cost', '>=', 47)
removeTable(temp_relation_after_join2)
# project result relation on the attribute 'sname', 'pname', 'cost'
result_relation_after_projection = project(temp_relation_after_selection, ['sname', 'pname', 'cost'])
removeTable(temp_relation_after_selection)
# display the result relation under folder queryOutput with name: queryResult.txt
open(os.path.join(query_output_path, query_result_page), "a").write(
    "e. For each supplier who supplied products with a cost of 47 or higher, list his/her name, product name and the cost.\n")
displayTable(result_relation_after_projection, query_result_page)
removeTable(result_relation_after_projection)

