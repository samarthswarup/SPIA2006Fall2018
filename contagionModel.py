import networkx as nx
import matplotlib.pyplot as plt
import random
from random import choice
import numpy as np
import pandas as pd
import socialnetwork as sn

NUM_RUNS = 1
NUMBER_OF_TIMESTEPS = 20 #years

SOCIAL_NETWORK_FILE = 'socialnetwork.gml'

INCARCERATION_DURATION_DISTRIBUTION = np.random.negative_binomial
nBlack = 1
pBlack = 0.0555
nWhite = 1
pWhite = 0.0665
P_CONTAGION_FILE = 'probabilities_of_contagion.txt'
pContagion = pd.read_csv(P_CONTAGION_FILE)
print(pContagion)

NUM_INITIAL_INCARCERATIONS = 50
S_COLOR = 'blue'
I_COLOR = 'red'

#Add comment here
def initialize(race):
    #set the initial states of all nodes in G to be S_COLOR
    nx.set_node_attributes(sn.G, S_COLOR, 'incarcerationState')
    
    #Add comment here
    candidates = [n for n in sn.G.nodes() if sn.G.nodes[n]['years'] > 17]
    
    for i in range(NUM_INITIAL_INCARCERATIONS):
        #Add comment here
        randomNode = choice(candidates)
        sn.G.node[randomNode]['incarcerationState'] = I_COLOR
        sn.G.node[randomNode]['start_step'] = -1
        if (race=='white'):
            sn.G.node[randomNode]['sentence_length'] = INCARCERATION_DURATION_DISTRIBUTION(nWhite, pWhite)
        else:
            sn.G.node[randomNode]['sentence_length'] = INCARCERATION_DURATION_DISTRIBUTION(nBlack, pBlack)

#Add comment here
def updateOneStep(num, prob, step):
    for n in sn.G.nodes():
        if ('incarcerationState' not in sn.G.node[n]):
            sn.G.node[n]['incarcerationState'] = S_COLOR
    
    #Add comment here
    nextState = {x:y['incarcerationState'] for x,y in sn.G.nodes(data=True)}
    # nextState = [y['incarcerationState'] for x,y in sn.G.nodes(data=True)]
    
    #Get all incarcerated nodes
    iNodes = [x for x,y in sn.G.nodes(data=True) if y['incarcerationState']==I_COLOR]
    
    for iNode in iNodes:
        gender = sn.G.node[iNode]['gender']
        
        #get the neighbors
        nbors = sn.G.neighbors(iNode)
        
        #if any are susceptible, make them incarcerated with probability depending on the relation
        for n in nbors:
            if (nextState[n] == S_COLOR):
                nborGender = sn.G.node[n]['gender']
                nborAge = sn.G.node[n]['years']
                relation = sn.G[iNode][n]['relation']
                p = -1
                if (relation=='IsChildOf'):
                    if (nborGender=='female'):
                        p=pContagion.loc[pContagion['relation']=='mother', gender].iloc[0]
                    else:
                        p=pContagion.loc[pContagion['relation']=='father', gender].iloc[0]
                elif (relation=='IsSiblingOf'):
                    if (nborAge > 17):
                        if (nborGender=='female'):
                            p=pContagion.loc[pContagion['relation']=='sister', gender].iloc[0]
                        else:
                            p=pContagion.loc[pContagion['relation']=='brother', gender].iloc[0]
                elif (relation=='IsSpouseOf'):
                    p=pContagion.loc[pContagion['relation']=='spouse', gender].iloc[0]
                elif (relation=='IsParentOf'):
                    if (nborAge > 17):
                        p=pContagion.loc[pContagion['relation']=='adult child', gender].iloc[0]
                elif (relation=='IsFriendOf'):
                    if (nborAge > 17):
                        if (nborGender=='female'):
                            p=pContagion.loc[pContagion['relation']=='sister', gender].iloc[0]
                        else:
                            p=pContagion.loc[pContagion['relation']=='brother', gender].iloc[0]
                if (p > 0):
                    if (random.random() < p):
                        nextState[n] = I_COLOR
        
        #Add comment here            
        if (sn.G.node[iNode]['start_step'] + sn.G.node[iNode]['sentence_length'] >= step):
            nextState[iNode] = S_COLOR
            del sn.G.node[iNode]['start_step']
            del sn.G.node[iNode]['sentence_length']
            
    #Copy over the nextState to the Graph                    
    for n in sn.G.nodes():
        sn.G.node[n]['incarcerationState'] = nextState[n]
        if ('start_step' not in sn.G.node[n] and sn.G.node[n]['incarcerationState']==I_COLOR):
            sn.G.node[n]['start_step'] = step
            sn.G.node[n]['sentence_length'] = INCARCERATION_DURATION_DISTRIBUTION(num, prob)
    
    #Add comment here    
    numIncarcerated = len([x for x,y in nextState.items() if y==I_COLOR])
    return numIncarcerated


################ Main program starts here

for run in range(NUM_RUNS):
    sn.readNetwork(SOCIAL_NETWORK_FILE)
    initialize('white')
    
    x=[0]
    y=[NUM_INITIAL_INCARCERATIONS]
    
    # Run one simulation
    for year in range(NUMBER_OF_TIMESTEPS):
        for month in range(12):
            numI = updateOneStep(nWhite, pWhite, year*12+month)
            x.append(year*12+month+1)
            y.append(numI)
            sn.updateGraphOneStep()
        sn.printCounts(year,month,False)
        
    # Plot the results of the current simulation as a line chart
    lines = plt.plot(x, y)
    plt.xlabel("Time step")
    plt.ylabel("Number incarcerated")
    plt.setp(lines, linewidth=1, color='b')
    plt.pause(1)
    
    #Add comment here
    sn.readNetwork(SOCIAL_NETWORK_FILE)
    initialize('black')
    
    x=[0]
    y=[NUM_INITIAL_INCARCERATIONS]
    
    # Run one simulation
    for year in range(NUMBER_OF_TIMESTEPS):
        for month in range(12):
            numI = updateOneStep(nBlack, pBlack, year*12+month)
            x.append(year*12+month+1)
            y.append(numI)
            sn.updateGraphOneStep()
        sn.printCounts(year,month,False)
        
    # Plot the results of the current simulation as a line chart
    lines = plt.plot(x, y)
    plt.xlabel("Time step")
    plt.ylabel("Number incarcerated")
    plt.setp(lines, linewidth=1, color='r')
    plt.pause(1)
    
plt.show()
