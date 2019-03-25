import networkx as nx
import matplotlib.pyplot as plt
import random
from random import choice
import numpy as np

NUMBER_OF_NODES = 1000
NUMBER_OF_EDGES = 5000

SHOW_GRAPH = False

NUM_RUNS = 25
NUMBER_OF_TIMESTEPS = 50


P_MIN = 0.01
P_MAX = 0.25
INCARCERATION_DURATION = 1

NUM_INITIAL_INCARCERATIONS = 2
S_COLOR = 'blue'
I_COLOR = 'red'

def initialize():
    #set the initial states of all nodes in G
    nx.set_node_attributes(G, S_COLOR, 'state')
    
    for i in range(NUM_INITIAL_INCARCERATIONS):
        randomNode = choice(list(G.nodes()))
        G.node[randomNode]['state'] = I_COLOR
        G.node[randomNode]['start_step'] = -1

def updateOneStep(p, step):
    nextState = [y['state'] for x,y in G.nodes(data=True)]
    
    #Get all incarcerated nodes
    iNodes = [x for x,y in G.nodes(data=True) if y['state']==I_COLOR]
    
    for iNode in iNodes:
        #get the neighbors
        nbors = G.neighbors(iNode)
        
        #if any are susceptible, make them incarcerated with probability P
        for n in nbors:
            if (nextState[n] == S_COLOR):
                if (random.random() < p):
                    nextState[n] = I_COLOR
                    
        if (G.node[iNode]['start_step'] + INCARCERATION_DURATION >= step):
            nextState[iNode] = S_COLOR
            del G.node[iNode]['start_step']
            
    #Copy over the nextState to the Graph                    
    for n in G.nodes():
        G.node[n]['state'] = nextState[n]
        if ('start_step' not in G.node[n] and G.node[n]['state']==I_COLOR):
            G.node[n]['start_step'] = step
        
        
    numIncarcerated = len([n for n in nextState if n==I_COLOR])
    return numIncarcerated

################ Main program starts here

G = nx.gnm_random_graph(NUMBER_OF_NODES, NUMBER_OF_EDGES)
prtext=None
x=[]
y=[]
for pr in np.linspace(P_MIN, P_MAX, num=NUM_RUNS):
    initialize()
    
    # Run one simulation with the current value of pr
    for i in range(NUMBER_OF_TIMESTEPS):
        numI = updateOneStep(pr, i)
        
    x.append(pr)
    y.append(numI)

plt.plot(x,y)
plt.xlabel("Probability")
plt.ylabel("Number incarcerated after 50 steps")
plt.show()