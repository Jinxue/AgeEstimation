'''
Created on Jul 28, 2015

@author: Jinxue Zhang

We compare our method with the existing network methods

We want to infer the age information by the neighbors.
Specifically, we keep 80% of the users as the training data, and then estimate the remaining 20% of users

The first is the paper from Liao et al to use the label propagation method.
'''

# Finds all maximal cliques in a graph using the Bron-Kerbosch algorithm. The input graph here is 
# in the adjacency list format, a dict with vertexes as keys and lists of their neighbors as values.
# https://en.wikipedia.org/wiki/Bron-Kerbosch_algorithm

from collections import defaultdict

def find_cliques(graph):
    p = set(graph.keys())
    r = set()
    x = set()
    cliques = []
    for v in degeneracy_ordering(graph):
        neighs = graph[v]
        find_cliques_pivot(graph, r.union([v]), p.intersection(neighs), x.intersection(neighs), cliques)
        p.remove(v)
        x.add(v)
    return sorted(cliques, key = lambda x: len(x), reverse = True)
    #return sorted(cliques, key=lambda x: len(x[1]), reverse = True)

def find_cliques_pivot(graph, r, p, x, cliques):
    if len(p) == 0 and len(x) == 0:
        cliques.append(r)
    else:
        u = iter(p.union(x)).next()
        for v in p.difference(graph[u]):
            neighs = graph[v]
            find_cliques_pivot(graph, r.union([v]), p.intersection(neighs), x.intersection(neighs), cliques)
            p.remove(v)
            x.add(v)

def degeneracy_ordering(graph):
    ordering = []
    ordering_set = set()
    degrees = defaultdict(lambda : 0)
    degen = defaultdict(list)
    max_deg = -1
    for v in graph:
        deg = len(graph[v])
        degen[deg].append(v)
        degrees[v] = deg
        if deg > max_deg:
            max_deg = deg

    while True:
        i = 0
        while i <= max_deg:
            if len(degen[i]) != 0:
                break
            i += 1
        else:
            break
        v = degen[i].pop()
        ordering.append(v)
        ordering_set.add(v)
        for w in graph[v]:
            if w not in ordering_set:
                deg = degrees[w]
                degen[deg].remove(w)
                if deg > 0:
                    degrees[w] -= 1
                    degen[deg - 1].append(w)
    
    ordering.reverse()
    return ordering

'''
x, y are dictionaries from the ground truth and estimated results.
'''
def confusionMatrix(x, y, g):
    
    # First generate the label vectors
    labelX = dict()
    labelY = dict()
    
    for user in x:
        if 1 <= g and x[user] <= 18:
            labelX[user] = 1
        elif 2 <= g and x[user] <= 22:
            labelX[user] = 2
        elif 3 <= g and x[user] <= 33:
            labelX[user] = 3
        elif 4 <= g and x[user] <= 45:
            labelX[user] = 4
        elif 5 <= g and x[user] <= 65:
            labelX[user] = 5
        elif 6 <= g:
            labelX[user] = 6

    for user in y:
        if 1 <= g and y[user] <= 18:
            labelY[user] = 1
        elif 2 <= g and y[user] <= 22:
            labelY[user] = 2
        elif 3 <= g and y[user] <= 33:
            labelY[user] = 3
        elif 4 <= g and y[user] <= 45:
            labelY[user] = 4
        elif 5 <= g and y[user] <= 65:
            labelY[user] = 5
        elif 6 <= g:
            labelY[user] = 6
    
    cm = []
    for i in range(g):
        cm.append([])
        for _ in range(g):
            cm[i].append(0)
    for user in x:
        cm[labelX[user] - 1][labelY[user] - 1] += 1
    
    #print cm
    for i in range(g):
        print cm[i]
    
import random
def LiaoMethod(ageF, netF, g):
    # First we build the network information
    graph = dict()
    userAge = dict()
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[str(ind)] = int(items[1])
        graph[str(ind)] = set()
        ind += 1
    
    for line in open(netF, 'rb'):
        items = line.split()
        if items[0] != items[1]:
            graph[items[0]].add(items[1])
            graph[items[1]].add(items[0])
    mc = find_cliques(graph)
    #print mc
    
    num = 0
    for clique in mc:
        if len(clique) > 1:
            #print clique
            num += 1
    print 'total users', len(graph), 'total cliques', len(mc), 'with effective', num
    
    # Then we assign the weight for each edge be the size of the maximum clique between user i and j
    weight = dict()
    for clique in mc:
        c_size = len(clique)
        if c_size > 1:
            for i in clique:
                if i not in weight:
                    weight[i] = dict()
                for j in clique:
                    if i != j and j not in weight[i]:
                        weight[i][j] = c_size
    
    p = dict()
    for i in weight:
        totW = sum(weight[i][x] for x in weight[i])
        p[i] = dict()
        for j in weight[i]:
            p[i][j] = 1.0 * weight[i][j] / totW
    
    # We then conduct the testing
    ratio = 0.8
    training = set(random.sample(set(userAge.keys()), int(len(userAge) * ratio)))
    testing = set(userAge.keys()) - training
    
    print 'Training users', len(training), 'Testing users', len(testing)
    testingAge = dict()
    old_size = len(testing) + 1
    while len(testing) < old_size:
        old_size = len(testing)
        ageTemp = dict()
        for user in testing:
            ageTemp[user] = dict()
        for user in training:
            if user not in p:
                continue
            for neighbor in p[user]:
                if neighbor not in training:
                    ageTemp[neighbor][user] = p[user][neighbor]
        for user in list(testing):
            if len(ageTemp[user]) == 0:
                continue
            testingAge[user] = max ( ageTemp[user][x] for x in ageTemp[user])
            testing.remove(user)
            training.add(user)
    print 'Find ages for ', len(testingAge), 'testing users by using algorithm MCAP.'
    # We then assign the average ages of the training dataset if a testing user has no neighbor
    meanAge = sum(userAge[x] for x in training) * 1.0 / len(training)
    print 'The average age for the training data:', meanAge
    
    for user in testing - set(testingAge.keys()):
        testingAge[user] = meanAge
    
    testingGTAge = dict()
    for user in testingAge:
        testingGTAge[user] = userAge[user]
    print 'Find ages for ', len(testingAge), 'testing users finally. With GT users', len(testingGTAge)
    # Finally we obtain the results
    
    confusionMatrix(testingGTAge, testingAge, g)
    
    return testingAge
                
    
threshold = 100
thFriends = 10
n = 30000
#ageFile = "L:\\Age\\Matlab\\ageUsers-t"+ str(threshold) + "-n" + str(n) + ".txt"
#netFile = "L:\\Age\\Matlab\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
g = 3
ageFile = "L:\\Age\\Matlab\\equal-ageUsers-t"+ str(threshold) + "-g" + str(g) + ".txt"
netFile = "L:\\Age\\Matlab\\equal-networkLocal-t"+ str(threshold) + "-g" + str(g) + ".txt"
LiaoMethod(ageFile, netFile, g)
