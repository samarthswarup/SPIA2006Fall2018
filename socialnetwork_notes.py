import networkx as nx
import random
from random import choice

INITIAL_NUM_NODES = 50
INITIAL_NUM_EDGES = 500

# Properties to model
# Age (Years, Months), Gender
# Parent, Child, Sibling, Friend

####### Life transitions
# Being born
#   Assign age (years=0, months=0)
#   Assign gender (random)
#   Create parent/child edges
#   Create sibling edges if necessary
# Starting school
#   When?
#   Assign friend edges (how many?)
# Starting college
#   When?
#   Remove some friend edges (how many?)
#   Add new friend edges (how many?)
# Starting work
#   When?
#   Remove some friend edges (how many?)
#   Add some friend edges (how many?)
# Getting married
#   When?
#   Add spouse edge (how to choose?)
# Having kids
#   When?
#   How many?
#   Add parent/child edges
# Retirement
#   Remove some friend edges (how many?)
# Death
#   Remove node and all edges

# Things we are not modeling for now
# Single parents
# Not going to school
# Not going to college
# Not working
# Not getting married
# Divorce



