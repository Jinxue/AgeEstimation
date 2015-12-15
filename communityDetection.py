'''
Created on Jul 12, 2015

@author: Jinxue Zhang 

compute the community structure by using Louvain's method
'''

import community
import networkx as nx
#import matplotlib.pyplot as plt

def genCommunity(netFile, outFile):
    G = nx.Graph()
    for line in open(netFile, 'rb'):
        items = line.split()
        if items[0] != items[1]:
            G.add_edge(items[0], items[1])
        # The separate node is a community
        else:
            G.add_node(items[0])
    
    print G.number_of_nodes(), 'nodes', G.number_of_edges(), 'edges.'
    
    #first compute the best partition
    partition = community.best_partition(G)
    
    '''
    #I always failed to install the numpy in Windows, so the code below could not be run
    #drawing
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G)
    count = 0.
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys()
                                    if partition[nodes] == com]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                    node_color = str(count / size))
    
    
    nx.draw_networkx_edges(G,pos, alpha=0.5)
    plt.show()
    '''
    
    
    comsWithNodes = dict()
    comsWithSize = dict()
    for node in partition:
        if partition[node] not in comsWithNodes:
            comsWithNodes[partition[node]] = set()
            comsWithSize[partition[node]] = 0
        comsWithNodes[partition[node]].add(node)
        comsWithSize[partition[node]] += 1
    
    print len(comsWithNodes), 'communities'
    
    comsWithSize_sorted = sorted(comsWithSize.items(), key=lambda x: x[1], reverse = True)
    
    '''
    WE construct the H matrix as follows:
    The output of the Louvain method partition numbers the community from 0 to the size
    x(i,j) represents that node j is in the community i
    '''
    outf = open(outFile, 'w')
    
    import math
    
    for comid, x in  comsWithSize_sorted:
        # Check the community number
    #    print >> outf, comid, x
        for node in comsWithNodes[comid]:
            # The regular community matrix
            #print >> outf, comid + 1, node, 1
            # The weighted community matrix
            print >> outf, comid + 1, node, 1.0 / math.sqrt(x) 
    outf.close()

'''
One idea is to refine the social network connections by removing the connections between different labels;
We could also add certain edges within the age groups
'''
def refNetwork(ageF, netF, outF, g, addEdges):
    userAge = dict()
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[ind] = int(items[1])
        ind += 1
    
    userGroup = dict()
    groupUser = dict()
    # We have six groups
    #groups = g
    for i in range(g):
        groupUser[i + 1] = set()
        
    for user in userAge:
        if 1 <= g and userAge[user] <= 18:
            userGroup[user] = 1
            groupUser[1].add(user)
        elif 2 <= g and userAge[user] <= 22:
            userGroup[user] = 2
            groupUser[2].add(user)
        elif 3 <= g and userAge[user] <= 33:
            userGroup[user] = 3
            groupUser[3].add(user)
        elif 4 <= g and userAge[user] <= 45:
            userGroup[user] = 4
            groupUser[4].add(user)
        elif 5 <= g and userAge[user] <= 65:
            userGroup[user] = 5
            groupUser[5].add(user)
        elif 6 <= g:
            userGroup[user] = 6
            groupUser[6].add(user)

    
    totalEdges = 0
    edgesSamelabel = 0
    #outf = open(outF, 'w')
    edges = set()
    for line in open(netF, 'rb'):
        items = line.split()
        if userGroup[int(items [0])] == userGroup[int(items [1])]:
            edgesSamelabel += 1
            edges.add(' '.join(items[0:2]))
            edges.add(' '.join([items[1], items[0]]))
            #print >> outf, line.rstrip('\r\n')
        totalEdges += 1
    print 'Total Users:' , len(userAge), 'Total edges:', totalEdges, 'Edges with the same labels:', edgesSamelabel

    # We then add addEdges from the same age group for each user
    import random
    for age in groupUser:
        for user in groupUser[age]:
            friends = groupUser[age]
            if len(friends) > addEdges:
                friends = set(random.sample(groupUser[age], addEdges))
            for user2 in friends:
                edges.add(' '.join([str(user), str(user2)]))
    print 'Total Edges after adding edges:', len(edges)

    outf = open(outF, 'w')
    for edge in edges:
        print >> outf, edge, 1
    

'''
We want to analyze the social network information
without community
'''
def homophilyEdge(ageF, netF, g):
    userAge = dict()
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[ind] = int(items[1])
        ind += 1
    
    print 'We have', len(userAge), 'users.'
    
    userGroup = dict()
    groupUser = dict()
    gapDist = dict()
    # We have six groups
    #groups = g
    for i in range(g):
        groupUser[i + 1] = set()
        
    for user in userAge:
        if 1 <= g and userAge[user] <= 18:
            userGroup[user] = 1
            groupUser[1].add(user)
        elif 2 <= g and userAge[user] <= 22:
            userGroup[user] = 2
            groupUser[2].add(user)
        elif 3 <= g and userAge[user] <= 33:
            userGroup[user] = 3
            groupUser[3].add(user)
        elif 4 <= g and userAge[user] <= 45:
            userGroup[user] = 4
            groupUser[4].add(user)
        elif 5 <= g and userAge[user] <= 65:
            userGroup[user] = 5
            groupUser[5].add(user)
        elif 6 <= g:
            userGroup[user] = 6
            groupUser[6].add(user)
    
    totalEdges = 0
    homophilyEdges = 0
    for line in open(netF, 'rb'):
        items = line.split()
        if items[0] != items[1]  and userGroup[int(items[0])] == userGroup[int(items[1])]:
            homophilyEdges += 1
        if items[0] != items[1]:
            ageGap = abs(userAge[int(items[0])] - userAge[int(items[1])])
            if ageGap not in gapDist:
                gapDist[ageGap] = 0
            gapDist[ageGap] += 1 
            totalEdges += 1
    print 'Total edges:', totalEdges, 'Edges with the same labels:', homophilyEdges, 'Ratio:', homophilyEdges * 1.0 / totalEdges
    print 'Age gap:', gapDist
    for gap in gapDist:
        print gap, gapDist[gap]

'''
We want to measure the similarity between any connected pair
'''
def homophilyTopic(ageF, netF, refF, g):
    userAge = dict()
    userId = dict()
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[ind] = int(items[1])
        userId[items[0]] = ind
        ind += 1
    
    print 'We have', len(userAge), 'users.'
    
    userGroup = dict()
    groupUser = dict()
    # We have six groups
    #groups = g
    for i in range(g):
        groupUser[i + 1] = set()
        
    for user in userAge:
        if 1 <= g and userAge[user] <= 18:
            userGroup[user] = 1
            groupUser[1].add(user)
        elif 2 <= g and userAge[user] <= 22:
            userGroup[user] = 2
            groupUser[2].add(user)
        elif 3 <= g and userAge[user] <= 33:
            userGroup[user] = 3
            groupUser[3].add(user)
        elif 4 <= g and userAge[user] <= 45:
            userGroup[user] = 4
            groupUser[4].add(user)
        elif 5 <= g and userAge[user] <= 65:
            userGroup[user] = 5
            groupUser[5].add(user)
        elif 6 <= g:
            userGroup[user] = 6
            groupUser[6].add(user)
    
    chosen = False
    userNum = 0
    userNGram = dict()
    for line in open(refF, 'rb'):
        if line[0] == "%":
            if "," not in line:
                user = line.rstrip('\r\n')[1:]
                if user in userId:
                    chosen = True
                else:
                    chosen = False
                    continue
                ngram = set()   # We create a new dict to record the ngram for this user
            elif chosen == True:
                userNum += 1
                if userNum % 1000 == 0:
                    print "We have processed ", userNum, 'users.'
                    
                # We then merge the ngram of this user to the whole ngram dict
                userNGram[userId[user]] = ngram
                #for ng in ngram:
                #    if ng not in idf:
                #        idf[ng] = 0
                #    idf[ng] += 1
                
        elif chosen == True:
            # We will consider unigram and digrams
            ngram |= set(line.split())

    print 'number of users have ngram:', len(userNGram)
    
    totalEdges = 0
    homophilyEdges = 0
    gapDist = dict()
    gapDiff = dict()
    #outf = open(outF, 'w')
    for line in open(netF, 'rb'):
        items = line.split()
        if items[0] != items[1]  and userGroup[int(items[0])] == userGroup[int(items[1])]:
            homophilyEdges += 1
        if items[0] != items[1]:
            ageGap = abs(userAge[int(items[0])] - userAge[int(items[1])])
            if ageGap not in gapDist:
                gapDist[ageGap] = 0
                gapDiff[ageGap] = 0.0
            gapDist[ageGap] += 1 
            totalEdges += 1
            
            a,b = len(userNGram[int(items[0])].intersection(userNGram[int(items[1])])), \
                    len(userNGram[int(items[0])].union(userNGram[int(items[1])]))
            jaccard = 1.0 * a / b
                         
            gapDiff[ageGap] += jaccard
            #print >> outf, jaccard
    print 'Total edges:', totalEdges, 'Edges with the same labels:', homophilyEdges, 'Ratio:', homophilyEdges * 1.0 / totalEdges
    print 'Age gap:', gapDist
    for gap in gapDist:
        print gap, gapDist[gap]
    for gap in gapDiff:
        print gap, gapDiff[gap] * 1.0 / gapDist[gap]
        
def homophily(ageF, netF, comF, g):
    userAge = dict()
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[ind] = int(items[1])
        ind += 1
    
    userGroup = dict()
    groupUser = dict()
    # We have six groups
    #groups = g
    for i in range(g):
        groupUser[i + 1] = set()
        
    for user in userAge:
        if 1 <= g and userAge[user] <= 18:
            userGroup[user] = 1
            groupUser[1].add(user)
        elif 2 <= g and userAge[user] <= 22:
            userGroup[user] = 2
            groupUser[2].add(user)
        elif 3 <= g and userAge[user] <= 33:
            userGroup[user] = 3
            groupUser[3].add(user)
        elif 4 <= g and userAge[user] <= 45:
            userGroup[user] = 4
            groupUser[4].add(user)
        elif 5 <= g and userAge[user] <= 65:
            userGroup[user] = 5
            groupUser[5].add(user)
        elif 6 <= g:
            userGroup[user] = 6
            groupUser[6].add(user)
    
    totalEdges = 0
    homophilyEdges = 0
    '''for line in open(netF, 'rb'):
        items = line.split()
        if items[0] != items[1]  and userGroup[int(items[0])] == userGroup[int(items[1])]:
            homophilyEdges += 1
        if items[0] != items[1]:
            totalEdges += 1
    print 'Total edges:', totalEdges, 'Edges with the same labels:', homophilyEdges, 'Ratio:', homophilyEdges * 1.0 / totalEdges'''

    '''
    We can also obtain the confusing matrix. 
    Note that since we sampled both the friends and the followers, there might be the case such that
    A is a mutual friend of B, but B has no mutual friend with A. So we need to notice this case.
    '''
    edges = set()
    for line in open(netF, 'rb'):
        items = line.split()
        if items[0] != items[1]:
            totalEdges += 1
            edges.add(' '.join(items[0:2]))
            edges.add(' '.join([items[1], items[0]]))
    print 'Total Users:' , ind - 1, 'Total edges:', totalEdges, 'Edges after adding up:', len(edges)
    
    confusionMatrix = []
    for i in range(g):
        confusionMatrix.append([])
        for _ in range(g):
            confusionMatrix[i].append(0)

    for edge in edges:
        items = edge.split()
        if userGroup[int(items[0])] == userGroup[int(items[1])]:
            homophilyEdges += 1
        confusionMatrix[userGroup[int(items[0])] - 1][userGroup[int(items[1])] - 1] += 1
    print 'Total edges:', len(edges) / 2, 'Edges with the same labels:', homophilyEdges / 2, 'Ratio:', homophilyEdges * 1.0 / len(edges)
    print 'Confusion Matrix: '
    for i in range(g):
        print confusionMatrix[i]
        
    '''
    We also need to analyze the homophily in the community
    '''
    print '\n\nThe distribution of age groups in each community ordered by the size decreasingly:'
    communities = dict()
    for line in open(comF, 'rb'):
        items = line.split()
        if items[0] not in communities:
            communities[items[0]] = set()
        communities[items[0]].add(int(items[1]))
    communities_sorted = sorted(communities.items(), key=lambda x: len(x[1]), reverse = True)
    comms = 0
    for cid, users in communities_sorted:
        if len(users) > 1:
            comms += 1
            print cid, len(users), len(groupUser[1].intersection(users)), len(groupUser[2].intersection(users)), len(groupUser[3].intersection(users)), \
                len(groupUser[4].intersection(users)), len(groupUser[5].intersection(users)), len(groupUser[6].intersection(users))
    print 'Total communities:', comms
    
threshold = 100
n = 60000
thFriends = 10
g = 3
#netFile = "L:\\Age\\Matlab\\ImpactSize\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
#outFile = "L:\\Age\\Matlab\\ImpactSize\\networkLocal-community-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
netFile = "L:\\Age\\Matlab\\equal-networkLocal-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
outFile = "L:\\Age\\Matlab\\equal-networkLocal-community-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
#netFile = "L:\\Age\\Matlab\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
#outFile = "L:\\Age\\Matlab\\networkLocal-community-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
genCommunity(netFile, outFile)

#g = 6
#ageFile = "L:\\Age\\Streams\\ageUsers-stream-refined4-t"+ str(threshold) + ".txt"
ageFile = "L:\\Age\\Matlab\\ageUsers-t"+ str(threshold) + "-n" + str(n) + ".txt"
#ageFile = "L:\\Age\\Final\\ageUsers-t"+ str(threshold) + "-n" + str(n) + ".txt"
#homophily(ageFile, netFile, outFile, g)

#-------------------------Only for data analysis--------------------------------------------------------------
#homophilyEdge("L:\\Age\\Final\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt", 
#               "L:\\Age\\Final\\networkLocal-t"+ str(threshold) + "-n60000-f" + str(thFriends) + ".txt", g)
#homophilyTopic("L:\\Age\\Final\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt", 
#               "L:\\Age\\Final\\networkLocal-t"+ str(threshold) + "-n60000-f" + str(thFriends) + ".txt", 
#               "L:\\Age\\Final\\refinedTweets-sample-t"+ str(threshold) + ".txt", g)
#---------------------------------------------------------------------------------------------------------------


addE = 0
# We only consider the edges with the same labels
out2File = "L:\\Age\\Matlab\\ref-networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + "-a" + str(addE) + ".txt"
out3File = "L:\\Age\\Matlab\\ref-networkLocal-community-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + "-a" + str(addE) + ".txt"
#refNetwork(ageFile, netFile, out2File, g, addE)
#genCommunity(out2File, out3File)
#homophily(ageFile, out2File, out3File, g)