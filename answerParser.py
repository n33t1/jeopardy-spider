import re

'''
@ input:
@ output:

"the subway (metro, transportation, or MTBA)"

what is MTBA => true
what is the metro => true

[subway, metro, transportation, mtba]

foreign words: words that contains weird symbols
'''

testCase1 = "the \"Fog\"   + - * \"Fog\"s"
s = "    tes!@#$%^&*(())___+t\" \"test1\" \"test3N"

# concert to lower case
s = s.lower()

# parse off beginning a, an, the
s = re.sub(r'^the |^an |^a', '', s)

# check if contains alternative answers aka ()s
# if re.find('()', s):
#       s = 

# remove all symbols 
s = re.sub('[^a-zA-Z]', '', s)

# remove all symbols but ()

# remove all space
a = strip()

print s



# "the/a/an hippopotamus"
# parse symbols: $, ', ., 

# (Samuel Taylor) Coleridge

# who is 

# what is
