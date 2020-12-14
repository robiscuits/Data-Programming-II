# Decision-Tree
The zipped file passed contains information on loans and bank decisions on them.
The python file contains several classes representing a diversity of function. The ZippedCSVReader iterates a zipped csv with skips.
Loan creates loan objects from the csv file. Bank iterates through the ZippedCSVReader to create loan objects.
BST and Node create a binary decision tree.
DTree uses the BST, which each loan object is then used on to determine whether the loan will be denied or approved.
Included are a RandomForest class and a BiasTesting class.
