import networkx as nx
import random
from random import choice
import numpy
import pandas as pd
import sys

INITIAL_POPULATION_SIZE = 1000
BURN_IN_PERIOD = 100 #years

P_ATTENDING_SCHOOL = 0.95

FRIEND_DISTRIBUTION = numpy.random.poisson

AVG_NUM_FRIENDS_IN_SCHOOL = 3
AVG_NUM_FRIENDS_NOT_IN_SCHOOL = 3
P_SYMMETRIC_FRIENDSHIP = 0.5

P_ATTENDING_COLLEGE = 0.8
AVG_NUM_FRIENDS_IN_COLLEGE = 3
AVG_NUM_FRIENDS_NOT_IN_COLLEGE = 3
P_DROPPING_SCHOOL_FRIENDS = 0.5

P_EMPLOYMENT = 0.2368
AVG_NUM_FRIENDS_WHEN_EMPLOYED = 3
AVG_NUM_FRIENDS_WHEN_UNEMPLOYED = 3
P_DROPPING_COLLEGE_FRIENDS = 0.5

P_GETTING_MARRIED = 0.006
MAX_SPOUSE_AGE_DIFFERENCE = 5 #years
P_DROPPING_FRIENDS_UPON_MARRIAGE = 0.3
P_GAINING_FRIENDS_FROM_SPOUSE = 0.3

P_FIRST_CHILD = 0.15
P_SECOND_CHILD = 0.1
P_THIRD_OR_GREATER_CHILD = 0.02

P_DROPPING_FRIENDS_ON_RETIREMENT = 0.7
AVG_NUM_FRIENDS_GAINED_ON_RETIREMENT = 2

P_DEATH_CSV_FILE = 'probability_of_death_by_age.csv'
pDeath = pd.read_csv(P_DEATH_CSV_FILE)

G = nx.DiGraph()
maxNodeID = 0

#Add comment here
def incrementAges():
    for node in G.nodes():
        G.nodes[node]['months'] += 1
        if (G.nodes[node]['months']==12):
            G.nodes[node]['years'] += 1
            G.nodes[node]['months'] = 0

#Add comment here
def birthModel(parent1, parent2):
    global maxNodeID
    child = maxNodeID
    maxNodeID += 1
    G.add_node(child)
    G.nodes[child]['years'] = 0
    G.nodes[child]['months'] = 0
    G.nodes[child]['gender'] = choice(['male', 'female'])
    G.nodes[child]['maritalStatus'] = 'unmarried'
    G.nodes[child]['numChildren'] = 0
    G.nodes[child]['status'] = 'PreSchool'
    
    G.nodes[parent1]['numChildren'] += 1
    G.nodes[parent2]['numChildren'] += 1
    
    #Add sibling edges if parents have other children
    siblings1 = [n for n in G.neighbors(parent1) \
                if G[parent1][n]['relation']=='IsParentOf']
    siblings2 = [n for n in G.neighbors(parent2) \
                 if G[parent2][n]['relation']=='IsParentOf']
    siblings = list(set(siblings1+siblings2))
    for sibling in siblings:
        G.add_edges_from([(sibling, child, {'relation':'IsSiblingOf'}), \
            (child, sibling, {'relation':'IsSiblingOf'})])

    #Add parent->child edge for both parents
    G.add_edges_from([(parent1, child, {'relation':'IsParentOf'}), \
        (parent2, child, {'relation':'IsParentOf'})])
    
    #Add child->parent edge for both parents
    G.add_edges_from([(child, parent1, {'relation':'IsChildOf'}), \
        (child, parent2, {'relation':'IsChildOf'})])

#Add comment here
def addFriendEdges(person, numEdgesToAdd, minFriendAge, maxFriendAge, status):
    global P_SYMMETRIC_FRIENDSHIP
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['years'] >= minFriendAge \
                  and G.nodes[n]['years'] <= maxFriendAge \
    and G.nodes[n]['status'] == status]
    
    #Add comment here
    if (len(candidates) > numEdgesToAdd):
        selectedCandidates = random.sample(candidates, numEdgesToAdd)
    else:
        selectedCandidates = candidates
        
    #Add comment here
    for c in selectedCandidates:
        if (G.has_edge(c, person) or G.has_edge(person, c)):
            continue
        G.add_edges_from([(c, person, {'relation':'IsFriendOf'})])
        if (random.random() < P_SYMMETRIC_FRIENDSHIP):
            G.add_edges_from([(person, c, {'relation':'IsFriendOf'})])

#Add comment here            
def dropFriendEdges(person, p):
    #Get all the current friends
    currentFriends = [n for n in G.predecessors(person) \
                      if G[n][person]['relation']=='IsFriendOf']
    
    #Add comment here
    for friend in currentFriends:
        if (random.random() < p):
            G.remove_edge(friend, person)

#Add comment here            
def startingSchoolModel():
    global P_ATTENDING_SCHOOL
    global FRIEND_DISTRIBUTION
    global AVG_NUM_FRIENDS_IN_SCHOOL
    global AVG_NUM_FRIENDS_NOT_IN_SCHOOL
    #Find all nodes that are exactly 5 years of age
    candidates = [n for n in G.nodes() if G.nodes[n]['years']==5 \
                  and G.nodes[n]['months']==0]
    
    #Add comment here
    for candidate in candidates:
        if (random.random() < P_ATTENDING_SCHOOL):
            G.nodes[candidate]['status']='InSchool'
            numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_IN_SCHOOL)
            addFriendEdges(candidate, numFriendsToAdd, 5, 6, 'InSchool')
        else:
            G.nodes[candidate]['status']='NotInSchool'
            numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_NOT_IN_SCHOOL)
            addFriendEdges(candidate, numFriendsToAdd, 5, 6, 'NotInSchool')

#Add comment here            
def startingCollegeModel():
    global P_ATTENDING_COLLEGE
    global AVG_NUM_FRIENDS_IN_COLLEGE
    global AVG_NUM_FRIENDS_NOT_IN_COLLEGE
    global P_DROPPING_SCHOOL_FRIENDS
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['years']==18 \
                  and G.nodes[n]['months']==0]
    
    #Add comment here
    for candidate in candidates:
        if (random.random() < P_ATTENDING_COLLEGE):
            G.nodes[candidate]['status'] = 'InCollege'
            numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_IN_COLLEGE)
            dropFriendEdges(candidate, P_DROPPING_SCHOOL_FRIENDS)
            addFriendEdges(candidate, numFriendsToAdd, 18, 21, 'InCollege')
        else:
            G.nodes[candidate]['status'] = 'NotInCollege'
            numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_NOT_IN_COLLEGE)
            dropFriendEdges(candidate, P_DROPPING_SCHOOL_FRIENDS)
            addFriendEdges(candidate, numFriendsToAdd, 18, 21, 'NotInCollege')

#Add comment here    
def startingWorkModel():
    global P_EMPLOYMENT
    global AVG_NUM_FRIENDS_WHEN_EMPLOYED
    global AVG_NUM_FRIENDS_WHEN_UNEMPLOYED
    global P_DROPPING_COLLEGE_FRIENDS
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['years']>=22 and \
                  G.nodes[n]['years']<25]
    
    #Add comment here
    for candidate in candidates:
        if (random.random()< P_EMPLOYMENT):
            G.nodes[candidate]['status'] = 'Working'
            numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_WHEN_EMPLOYED)
            dropFriendEdges(candidate, P_DROPPING_COLLEGE_FRIENDS)
            addFriendEdges(candidate, numFriendsToAdd, 22, 65, 'Working')
        else:
            G.nodes[candidate]['status'] = 'NotWorking'
            
    #Add comment here
    candidatesNotWorking = [n for n in G.nodes if G.nodes[n]['years']==25 and \
                            G.nodes[n]['months']==0 and \
    G.nodes[n]['status']=='NotWorking']
    
    #Add comment here
    for candidate in candidatesNotWorking:
        numFriendsToAdd = FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_WHEN_UNEMPLOYED)
        dropFriendEdges(candidate, P_DROPPING_COLLEGE_FRIENDS)
        addFriendEdges(candidate, numFriendsToAdd, 22, 65, 'NotWorking')

#Add comment here
def findMatch(person):
    global MAX_SPOUSE_AGE_DIFFERENCE
    age = G.nodes[person]['years']
    gender = G.nodes[person]['gender']
    #Add comment here
    candidateMatches = [n for n in G.nodes() if G.nodes[n]['years'] >= 18 and \
                        abs(G.nodes[n]['years']-age) <= MAX_SPOUSE_AGE_DIFFERENCE and \
    G.nodes[n]['gender']!=gender and G.nodes[n]['maritalStatus']=='unmarried']
    
    #Add comment here
    for candidate in candidateMatches:
        if (G.has_edge(candidate, person)):
            if (G[candidate][person]['relation']!='IsFriendOf'):
                candidateMatches.remove(candidate)
    
    #Add comment here
    chosenMatch = -1
    if candidateMatches:
        chosenMatch = choice(candidateMatches)
    
    return chosenMatch

#Add comment here    
def gettingMarriedModel():
    global P_GETTING_MARRIED
    global P_DROPPING_FRIENDS_UPON_MARRIAGE
    global P_GAINING_FRIENDS_FROM_SPOUSE
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['years'] >= 18 and \
                  G.nodes[n]['maritalStatus']=='unmarried']
    
    #Add comment here
    for candidate in candidates:
        if (random.random() < P_GETTING_MARRIED and G.nodes[candidate]['maritalStatus']=='unmarried'):
            match = findMatch(candidate)
            #Add comment here
            if match != -1:
                G.nodes[candidate]['maritalStatus']='married'
                G.nodes[match]['maritalStatus']='married'
                if (G.has_edge(candidate, match)):
                    G.remove_edge(candidate, match)
                if (G.has_edge(match, candidate)):
                    G.remove_edge(match, candidate)
                G.add_edges_from([(candidate, match, {'relation':'IsSpouseOf'}), \
                    (match, candidate, {'relation':'IsSpouseOf'})])
                
                #Add comment here
                candidateParents = [n for n in G.predecessors(candidate) if G[n][candidate]['relation']=='IsParentOf']
                matchParents = [n for n in G.predecessors(match) if G[n][match]['relation']=='IsParentOf']
                for parent in candidateParents:
                    G.add_edges_from([(parent, match, {'relation':'IsParentInLawOf'}), \
                        (match, parent, {'relation':'IsChildInLawOf'})])
                for parent in matchParents:
                    G.add_edges_from([(parent, candidate, {'relation':'IsParentInLawOf'}), \
                        (candidate, parent, {'relation':'IsChildInLawOf'})])
                
                #Add comment here    
                candidateSiblings = [n for n in G.predecessors(candidate) if G[n][candidate]['relation']=='IsSiblingOf']
                matchSiblings = [n for n in G.predecessors(match) if G[n][match]['relation']=='IsSiblingOf']
                for sibling in candidateSiblings:
                    G.add_edges_from([(sibling, match, {'relation':'IsSiblingInLawOf'}), \
                        (match, sibling, {'relation':'IsSiblingInLawOf'})])
                for sibling in matchSiblings:
                    G.add_edges_from([(sibling, candidate, {'relation':'IsSiblingInLawOf'}), \
                        (candidate, sibling, {'relation':'IsSiblingInLawOf'})])
                
                #Add comment here    
                dropFriendEdges(candidate, P_DROPPING_FRIENDS_UPON_MARRIAGE)
                dropFriendEdges(match, P_DROPPING_FRIENDS_UPON_MARRIAGE)
                #Add comment here
                candidateFriends = [n for n in G.predecessors(candidate) if G[n][candidate]['relation']=='IsFriendOf']
                matchFriends = [n for n in G.predecessors(match) if G[n][match]['relation']=='IsFriendOf']
                for friend in candidateFriends:
                    if (random.random() < P_GAINING_FRIENDS_FROM_SPOUSE and friend!=match):
                        if (G.has_edge(friend, match) or G.has_edge(match, friend)):
                            continue
                        G.add_edges_from([(friend, match, {'relation':'IsFriendOf'}), \
                            (match, friend, {'relation':'IsFriendOf'})])
                for friend in matchFriends:
                    if (random.random() < P_GAINING_FRIENDS_FROM_SPOUSE and friend!=candidate):
                        if (G.has_edge(candidate, match) or G.has_edge(match, candidate)):
                            continue
                        G.add_edges_from([(friend, candidate, {'relation':'IsFriendOf'}), \
                            (candidate, friend, {'relation':'IsFriendOf'})])
                        
#Add comment here
def havingChildrenModel():
    global P_FIRST_CHILD
    global P_SECOND_CHILD
    global P_THIRD_OR_GREATER_CHILD
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['gender']=='female' and \
                  G.nodes[n]['years']>=18 and G.nodes[n]['years']<=40 and \
    G.nodes[n]['maritalStatus']=='married']
    
    #Add comment here
    for candidate in candidates:
        spouse = [n for n in G.predecessors(candidate) if G[n][candidate]['relation']=='IsSpouseOf']
        #Add comment here
        if (G.nodes[candidate]['numChildren']==0):
            if (random.random() < P_FIRST_CHILD):
                try:
                    birthModel(candidate, spouse[0])
                except IndexError:
                    print("IndexError:")
                    print('Candidate =',candidate)
                    print('Node attributes:',G.nodes[candidate])
                    print('Neighbors:',G[candidate])
                    sys.exit()
        #Add comment here
        elif (G.nodes[candidate]['numChildren']==1):
            child = [n for n in G.predecessors(candidate) if G[n][candidate]['relation']=='IsChildOf']
            if (random.random() < P_SECOND_CHILD and G.nodes[child[0]]['years']>=1):
                try:
                    birthModel(candidate, spouse[0])
                except IndexError:
                    print("IndexError:")
                    print('Candidate =',candidate)
                    print('Node attributes:',G.nodes[candidate])
                    print('Neighbors:',G[candidate])
                    sys.exit()
        #Add comment here
        else:
            childrenAges = [G.nodes[n]['years'] for n in G.predecessors(candidate) \
                            if G[n][candidate]['relation']=='IsChildOf']
            minAge = min(childrenAges)
            if (random.random() < P_THIRD_OR_GREATER_CHILD and minAge >= 1):
                try:
                    birthModel(candidate, spouse[0])
                except IndexError:
                    print("IndexError:")
                    print('Candidate =',candidate)
                    print('Node attributes:',G.nodes[candidate])
                    print('Neighbors:',G[candidate])
                    sys.exit()
                
#Add comment here
def retirementModel():
    global P_DROPPING_FRIENDS_ON_RETIREMENT
    global FRIEND_DISTRIBUTION
    global AVG_NUM_FRIENDS_GAINED_ON_RETIREMENT
    #Add comment here
    candidates = [n for n in G.nodes() if G.nodes[n]['years']==65 and G.nodes[n]['months']==0]
    
    #Add comment here
    for candidate in candidates:
        G.nodes[candidate]['status']='Retired'
        dropFriendEdges(candidate, P_DROPPING_FRIENDS_ON_RETIREMENT)
        addFriendEdges(candidate, FRIEND_DISTRIBUTION(AVG_NUM_FRIENDS_GAINED_ON_RETIREMENT), \
                       65, 100, 'Retired')

#Add comment here
def deathModel():
    for node in list(G.nodes()):
        age = G.nodes[node]['years']
        prob = 0.9
        if (age < 101):
            #Add comment here
            prob = pDeath.loc[pDeath['age']==age, 'probability'].iloc[0]
        if (random.random() < prob):
            #Add comment here
            if (G.nodes[node]['maritalStatus']=='married'):
                spouse = [n for n in G.successors(node) if G[node][n]['relation']=='IsSpouseOf']
                if (len(spouse) != 1):
                    print("Node",node,"has",len(spouse),"spouses!")
                    print("Node attributes:",G.nodes[node])
                    print("Neighbors:",G[node])
                    for sp in spouse:
                        print("Node attributes:",G.nodes[sp])
                        print("Neighbors:",G[sp])
                    sys.exit(1)
                G.nodes[spouse[0]]['maritalStatus']='unmarried'
                # print('Marital status for',spouse[0],'set to unmarried.')
            #Add comment here
            parents = [n for n in G.successors(node) if G[node][n]['relation']=='IsChildOf']
            #Add comment here
            if parents:
                for parent in parents:
                    G.nodes[parent]['numChildren']-=1
            G.remove_node(node)
        
#Add comment here
def burnIn():
    global BURN_IN_PERIOD
    printCounts(0,0,True)
    for years in range(BURN_IN_PERIOD):
        for months in range(12):
            updateGraphOneStep()
        printCounts(years,months,False)

#Add comment here
def updateGraphOneStep():
    startingSchoolModel()
    startingCollegeModel()
    startingWorkModel()
    gettingMarriedModel()
    havingChildrenModel()
    retirementModel()
    deathModel()
    incrementAges()

#Add comment here
def createInitialPopulation():
    global INITIAL_POPULATION_SIZE
    global maxNodeID
    for i in range(INITIAL_POPULATION_SIZE):
        G.add_node(i)
        G.nodes[i]['years'] = random.randrange(5)
        G.nodes[i]['months'] = random.randrange(11)
        G.nodes[i]['gender'] = choice(['male', 'female'])
        G.nodes[i]['maritalStatus'] = 'unmarried'
        G.nodes[i]['numChildren'] = 0
        G.nodes[i]['status'] = 'PreSchool'
    maxNodeID = INITIAL_POPULATION_SIZE

#Add comment here
def printCounts(year, month, printHeader):
    if (printHeader):
        print('Year,Month,Number_of_nodes,Number_of_edges,Number_of_children,Number_of_adults,' + \
              'Number_married,Number_in_school,Number_working,Number_retired,Number_of_parents')
    numChildren = len([n for n in G.nodes() if G.nodes[n]['years'] < 18])
    numAdults = len([n for n in G.nodes() if G.nodes[n]['years'] > 17])
    numMarried = len([n for n in G.nodes() if G.nodes[n]['maritalStatus'] == 'married'])
    numInSchool = len([n for n in G.nodes() if G.nodes[n]['status']=='InSchool'])
    numWorking = len([n for n in G.nodes() if G.nodes[n]['status']=='Working'])
    numRetired = len([n for n in G.nodes() if G.nodes[n]['status']=='Retired'])
    numParents = len([n for n in G.nodes() if G.nodes[n]['numChildren'] > 0])
    print(year,month,G.number_of_nodes(), G.number_of_edges(), numChildren, numAdults, numMarried, \
          numInSchool, numWorking, numRetired, numParents, sep=',', end='\n')

def writeNetwork(filename):
    nx.write_gml(G, filename)
    
def readNetwork(filename):
    global maxNodeID
    global G
    G = nx.read_gml(filename)
    maxNodeID=0
    
    #Add comment here
    for node in G.nodes():
        if (maxNodeID < int(node)):
            maxNodeID = int(node)
            
    #Add comment here
    maxNodeID += 1
    printCounts(0,0,True)

#Add comment here
if __name__ == "__main__":
    createInitialPopulation()
    writeNetwork('socialNetworkInitial.gml')
    burnIn()
    writeNetwork('socialNetwork.gml')

# Properties to model: Node attributes
# Age: Years and Months
# Gender: Male or Female
# 
# Relationships to model: Edge attributes (directed graph)
# Parent-child
# Siblings
# Friends
# 
# Life transitions to model:
# Birth
#     Create a new node in the graph
#     Assign age: years=0, months=0
#     Assign gender: random
#     Assign parent edges (and edges from the parents to this child)
#     Assign sibling edges (if necessary)
# Starting school
#     When?
#     Add friend edges (How many? How to choose? Friend ages?)
#     Extra-curriculars
# Starting college
#     When?
#     Add friend edges (How many? How to choose? Friend ages?)
#     Remove some earlier friend edges (How many? How to choose? Friend ages?)
#     Leaving childhood home
# Starting work
#     When?
#     Add friend edges (How many? How to choose? Friend ages?)
#     Remove some earlier friend edges (How many? How to choose? Friend ages?)
# Getting married
#     When?
#     Add spouse edge (How to choose? Spouse age?)
#     Add in-law edges
#     Add friend edges (How many? How to choose? Friend ages?)
#     Remove some earlier friend edges (How many? How to choose? Friend ages?)
# Having children
#     When?
#     How many?
#     Add friend edges (How many? How to choose? Friend ages?)
#     Remove some earlier friend edges (How many? How to choose? Friend ages?)
# Retirement
#     When?
#     Lose several friend edges (How many? How to choose? Friend ages?)
#     Add a few friend edges (How many? How to choose? Friend ages?)
# Death
#     Remove node and all associated edges
# 
# Possible things to add to the model
# Disability
# Wealth
# Parent socio-economic status
# Sexual orientation
# Same-sex marriage
# 
# Things we are not modeling
# Not going to school
# Not going to college
# Not working
# Not getting married(?)
# Not having kids(?)
#     Single parents(?)
# Divorce
