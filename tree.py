# project: p2
# submitter: rrgeorge
# partner: none


from io import TextIOWrapper
from zipfile import ZipFile
import csv, re
class ZippedCSVReader:
    def __init__(self, filename):
        self.filename = filename
        with ZipFile(filename) as zf:
            self.paths = zf.namelist()
            self.paths.sort()
    
    def lines(self, name):
        with ZipFile(self.filename) as zf:
            with zf.open(name) as f:
                for line in TextIOWrapper(f):
                    yield line
                    
    def csv_iter(self, name = None):
        if name == None:
            with ZipFile(self.filename) as zf:
                for file in self.paths:
                    with zf.open(file, "r") as ifile:
                        for reader in csv.DictReader(TextIOWrapper(ifile), delimiter = ","):
                            yield reader
            
        else:
            with ZipFile(self.filename) as zf:
                with zf.open(name, "r") as ifile:
                    for reader in csv.DictReader(TextIOWrapper(ifile), delimiter = ","):
                        yield reader
                        
class Loan():
    def __init__(self, amount, purpose, race, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.income = income
        self.decision = decision
        self.loan = {"amount": amount, "purpose": purpose, "race": race, "income": income, "decision": decision}

    def __repr__(self):
        #values = list(self.dict.values())
        return f"Loan({self.amount}, '{self.purpose}', '{self.race}', {self.income}, '{self.decision}')"

    def __getitem__(self, lookup):
        if lookup in self.loan.keys():
            return self.loan[lookup]
        if lookup in self.loan.values():
            return 1
        else:
            return 0
        
loan = Loan(40, "Home improvement", "Asian", 120, "approve")
loan["Home improvement"]

def get_bank_names(reader, filename = None):
    agency_abbr = []
    if filename == None:
        for row in reader.csv_iter():
            abbr = row.get("agency_abbr")
            if abbr != None and abbr not in agency_abbr:
                agency_abbr.append(abbr)
    else:
        for row in reader.csv_iter(filename):
            abbr = row.get("agency_abbr")
            if abbr != None and abbr not in agency_abbr:
                agency_abbr.append(abbr)
                
    agency_abbr.sort()
    return agency_abbr 

class Bank:
    def __init__(self, bname, reader):
        self.reader = reader
        self.bname = bname
        
    def loan_iter(self):
        if self.bname != None:
            for line in self.reader.csv_iter():
                if line.get("agency_abbr") == self.bname:
                    if line.get("loan_amount_000s") == "":
                        ro = 0
                    else:
                        ro = int(line.get("loan_amount_000s"))
                    if line.get("applicant_income_000s") == "":
                        io = 0
                    else:
                        io = int(line.get("applicant_income_000s"))
                    line1 = Loan(int(ro), line.get("loan_purpose_name"), line.get("applicant_race_name_1"), int(io), line.get("action_taken_name"))
                    yield line1
        else:      
            for line in self.reader.csv_iter():
                if line.get("loan_amount_000s") == "":
                    ro = 0
                else:
                    ro = int(line.get("loan_amount_000s"))
                if line.get("applicant_income_000s") == "":
                    io = 0
                else:
                    io = int(line.get("applicant_income_000s"))
                line1 = Loan(int(ro), line.get("loan_purpose_name"), line.get("applicant_race_name_1"), int(io), line.get("action_taken_name"))
                yield line1
    
    def loan_filter(self, loan_min, loan_max, loan_purpose):
        for line in self.loan_iter():
            if line.amount >= loan_min and line.amount <= loan_max and loan_purpose == line.purpose:
                yield line
    
reader = ZippedCSVReader('mini.zip')
b = Bank("HUD", reader)
for loan in b.loan_iter():
    pass
for loan in b.loan_filter(100, 300, '3'):
    pass

class SimplePredictor():
    i = 0
    def predict(self, loan):
        if loan["purpose"] == "Home improvement":
            SimplePredictor.i += 1
            return True
        return False
    def getApproved(self):
        return SimplePredictor.i

class Node():
    def __init__(self, input_string, root = False):
        if root == True:
            string = list(input_string.keys())[0]
        else:
            string = list(input_string.values())[0]
            
        self.depth = string.count("|") -1 
        self.key = re.findall('-- (.*)(?: >| <|:)', string)[0]
        self.val = re.findall('\d+', string)[0]
        if self.key == "amount" or self.key == "income":
            self.val = int(self.val)
        self.left = None
        self.right = None
        self.parent = None
        
class BST():
    def __init__(self):
        self.root = None
        self.size = 0
        self.previous = None
    
    def __nextOpen(self, node):
        if node == None:
            return
        if node.left != None and node.right != None:
            self.__nextOpen(node.parent)
        else:
            self.previous = node
            
    def add(self, node):
        if self.previous == None:
            self.root = node
            self.previous = node
            self.size += 1
        elif self.previous.depth >= node.depth: #switch parent node
            self.__nextOpen(self.previous.parent)
        elif self.previous.depth < node.depth: #add child
            if self.previous.left == None:
                self.previous.left = node
            else:
                assert self.previous.right == None
                self.previous.right = node
            node.parent = self.previous
            self.previous = node
            self.size += 1
            
    def predict(self, loan):
        current = self.root
        while current.key != "class":
            if current.key == "amount" or current.key == "income":
                if loan[current.key] <= current.val:
                    current = current.left
                else:
                    current = current.right
            else:
                if loan[current.key] <= int(current.val):
                    current = current.left
                else:
                    current = current.right
        return current.val 
    
    def __dump(self, node):
        if node == None: 
            return
        self.__dump(node.left) 
        self.__dump(node.right)
        
    def dump(self):
         self.__dump(self.root)

class DTree(SimplePredictor):
    def __init__(self):
        self.trees = BST()
        self.disapproved = 0
        self.approved = 0
    
    def readTree(self, reader, path):
        for row in reader.csv_iter(path):
            if self.trees.root == None:
                self.trees.add(Node(row, root = True))
            self.trees.add(Node(row, root = False))
    
    def predict(self, data):
        result = self.trees.predict(data)
        if result == '0':
            self.disapproved += 1
            return False
        else:
            self.approved += 1
            return True
    
    def getDisapproved(self):
        return self.disapproved
    def getApproved(self):
        return self.approved
    
    def dump(self):
        self.trees.dump()
     
    
class RandomForest(SimplePredictor):
    def __init__(self, trees):
        #trees: a list of DTree instances that will "vote"
        self.trees = trees
        self.approvals = 0
        self.denials = 0
        
    def predict(self, loan):
        #takes votes and returns majority opinion
        for tree in self.trees:
            tree.predict(loan)
            self.approvals += tree.approved
            self.denials += tree.disapproved
            
        if self.approvals > self.denials:
            return True
        else:
            return False
        

def bias_test(bank, predictor, race_override):
    li = bank.loan_iter()
    racism_tally = 0
    i = 0
    for l in li:
        i+=1
        if predictor.predict(l) == True:
            new_l = Loan(l["amount"], l["purpose"], race_override, l["income"], l["decision"])
            if predictor.predict(new_l) == False:
                racism_tally +=1
                
    return racism_tally/i
