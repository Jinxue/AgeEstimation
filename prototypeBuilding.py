'''
Created on Jul 7, 2015

@author: Jinxue Zhang

We build a prototype on the sampled and small dataset. The basic step is:
1. sample 5000 users from "L:\\Age\\Streams\\ageUsers-stream-refined4-t"+ str(threshold) + ".txt"
2. Build the label matrix, which is 5000 x 6 of size, corresponding to 6 groups. Aij = 1 if user i in group j.
3. Build the TF-IDF matrix for these 5000 users.

'''

'''
Sample the users and then build the label matrix
ageFile: the file with the whole aged users
n: the number of the sampled users
output: a sampled user file and a matrix file
'''
import random
def sampleAndLabel(ageF, out1F, out2F, n):
    userAge = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = int(items[1])
    
    #sampledUser = set()
    if n < len(userAge):
        sampledUser = set(random.sample(set(userAge.keys()), n))
    else:
        sampledUser = set(userAge.keys())
    
    outf1 = open(out1F, 'w')
    outf2 = open(out2F, 'w')
    distR = [0, 0, 0, 0, 0, 0]  # Represent six groups
    for line in open(ageF, 'rb'):
        user = line.split("::")[0]
        if user in sampledUser:
            print >> outf1, line.rstrip('\r\n')
            
            if userAge[user] <= 18:
                distR[0] += 1
                print >> outf2, 1, 0, 0, 0, 0, 0
            elif userAge[user] <= 22:
                distR[1] += 1
                print >> outf2, 0, 1, 0, 0, 0, 0
            elif userAge[user] <= 33:
                distR[2] += 1
                print >> outf2, 0, 0, 1, 0, 0, 0
            elif userAge[user] <= 45:
                distR[3] += 1
                print >> outf2, 0, 0, 0, 1, 0, 0
            elif userAge[user] <= 65:
                distR[4] += 1
                print >> outf2, 0, 0, 0, 0, 1, 0
            else:
                distR[5] += 1
                print >> outf2, 0, 0, 0, 0, 0, 1
     
    outf1.close()
    outf2.close()
    print distR, sum(distR)
    
'''
One big problem is that the dataset is highly biased, shown as follows:
[0.5340    0.3987    0.0526    0.0104    0.0042    0.0000]
[1461, 1461, 1461, 287, 117, 1]

which about 90% of the users are in the first and the second groups. 
In this case, we aim to create dataset with each group of each size.
Specifically, we use the number of users in the fifth group as the benchmark 
to sample the first to thrid group.
'''
def equalSample(ageF, out1F, out2F, g):
    userAge = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = int(items[1])
    
    userGroup = dict()
    
    # We have six groups
    groups = g
    for i in range(groups):
        userGroup[i + 1] = set()
        
    for user in userAge:
        if 1 <= g and userAge[user] <= 18:
            userGroup[1].add(user)
        elif 2 <= g and userAge[user] <= 22:
            userGroup[2].add(user)
        elif 3 <= g and userAge[user] <= 33:
            userGroup[3].add(user)
        elif 4 <= g and userAge[user] <= 45:
            userGroup[4].add(user)
        elif 5 <= g and userAge[user] <= 65:
            userGroup[5].add(user)
        elif 6 <= g:
            userGroup[6].add(user)
    
    glen = []
    for i in range(groups):
        glen.append(len(userGroup[i + 1]))

    print glen
    
    benchmark = len(userGroup[3])    
    
    outf1 = open(out1F, 'w')
    outf2 = open(out2F, 'w')
    distR = []
    for i in range(groups):
        distR.append(0) 
    sampledUser = set()
    for ag in userGroup:
        users = userGroup[ag]
        if len(users) > benchmark:
            users = set(random.sample(users, benchmark))
        sampledUser |= users
        
        outList = []
        for i in range(groups):
            if i == (ag - 1):
                outList.append('1')
            else:
                outList.append('0')
        for user in users:
            print >> outf2, ' '.join(outList)
        distR[ag - 1] = len(users) 

    for line in open(ageF, 'rb'):
        user = line.split("::")[0]
        if user in sampledUser:
            print >> outf1, line.rstrip('\r\n')
            
    outf1.close()
    outf2.close()
    
    print '---------------Finish the equal sampling------------------'
    print distR
    
'''
Then we build the TF-IDF matrix for the sampled users.
We use the f(t,d) log (N / nt).

Before that, we need to find out the features, the top-10000 unigrams and digrams
'''
from GTAnalysis import ngrams_stats_init_by_age_wo_repeat, TFIDF, TFIDFForFriends
def findFeatures(refF, ageF, outF1, nFeatures, uniR):
    print "***************Finding the features*********************************"
    outf = open(outF1, 'w')
    #chosenNGs = set()
    
    #uniR = 0.5
    nf = [int(nFeatures * uniR), nFeatures - int(nFeatures * uniR) ]
    for n in [1, 2]:
    #for n in [2]:
        ageNGram, _ = ngrams_stats_init_by_age_wo_repeat(refF, ageF, n)
        # We then obtaint he top 5000 terms
        termDict = dict()
        for age in ageNGram:
            ngram = ageNGram[age]
            for ng in ngram:
                if ng not in termDict:
                    termDict[ng] = 0
                termDict[ng] += ngram[ng]
        ordered = sorted(termDict.items(), key=lambda x: x[1], reverse=True)
        #print >> outf, "## ngram = " + str(n)
        ind = 0
        for t,x in ordered:
            #if ind < int(nFeatures / 2):
            if ind < nf[n - 1]:
            #if ind < nFeatures:
                print >> outf, t, x
                #chosenNGs.add(t)
                ind += 1 
    outf.close()
    

'''
Generate the sparse ARFF file for the Weka
rawFile: the original TF-IDF file
labelFile: the file for tha label
n: the number of the users
m: the number of the features
outFile: the generated ARFF file
'''
def generateForWeka(rawFile, labelFile, n, m, outFile):
    
    
    tfidf = dict()
    for line in open(rawFile, 'rb'):
        items = line.split()
        user = int(items[0]) - 1
        if user not in tfidf:
            tfidf[user] = dict()
        tfidf[user][int(items[1]) - 1] = items[2]
    
    tfidf_sorted = sorted(tfidf.items(), key=lambda x: x[0])
    print 'Load feature data for', len(tfidf), 'users.'
    
    label = dict()
    ind = 0
    for line in open(labelFile, 'rb'):
        label[ind] = line.rstrip('\r\n').split().index("1") + 1
        ind += 1
    print 'Load label data for', len(label), 'users.'
    
    
    outf = open(outFile, 'w')
    
    print >> outf, "%Title: Age estimation"
    print >> outf, "@RELATION AgeEstimation\n"
    
    for i in range(m):
        print >> outf, "@ATTRIBUTE", i, "NUMERIC"
    print >> outf, "@ATTRIBUTE class {1,2,3,4,5,6}"
    
    print >> outf, "\n@DATA"
    for user,conn in tfidf_sorted:
        x = "{"
        conn_sorted = sorted(conn.items(), key=lambda x: x[0])
        for u, v in conn_sorted:
            x += str(u) + " " + v + ','
        x += str(m) + " " + str(label[user])
        x += "}"    
        print >> outf, x
    outf.close()

def generateByNetworkForWeka(rawFile, labelFile, outFile):
    
    tfidf = dict()
    for line in open(rawFile, 'rb'):
        items = line.split()
        user = int(items[0]) - 1
        if user not in tfidf:
            tfidf[user] = dict()
        tfidf[user][int(items[1]) - 1] = items[2]
    
    tfidf_sorted = sorted(tfidf.items(), key=lambda x: x[0])
    print 'Load feature data for', len(tfidf), 'users.'
    
    label = dict()
    ind = 0
    for line in open(labelFile, 'rb'):
        label[ind] = line.rstrip('\r\n').split().index("1") + 1
        ind += 1
    print 'Load label data for', len(label), 'users.'
    n = len(label)
    
    outf = open(outFile, 'w')
    
    print >> outf, "%Title: Age estimation"
    print >> outf, "@RELATION AgeEstimation\n"
    
    for i in range(n):
        print >> outf, "@ATTRIBUTE", i, "NUMERIC"
    print >> outf, "@ATTRIBUTE class {1,2,3,4,5,6}"
    
    print >> outf, "\n@DATA"
    for user,conn in tfidf_sorted:
        x = "{"
        conn_sorted = sorted(conn.items(), key=lambda x: x[0])
        for u, v in conn_sorted:
            x += str(u) + " " + v + ','
        x += str(n) + " " + str(label[user])
        x += "}"    
        print >> outf, x
    outf.close()
    
threshold = 100
n = 50000

# First we sample the users and fix it by the numbers
ageFile = "L:\\Age\\Final\\ageUsers-stream-refined4-t"+ str(threshold) + ".txt"
refFile = "L:\\Age\\Final\\refinedTweets-sample-t"+ str(threshold) + ".txt"

# Network information
friendFile = "L:\\Age\\Final\\friends\\Friends-ageUsers-stream.txt"
followerFile = "L:\\Age\\Final\\friends\\Followers-ageUsers-stream.txt"
outFriendsFileRef = "L:\\Age\\Streams\\friends\\mutualFriends-refined.txt"
refTweetsDir = 'L:\\Age\\Streams\\friends\\ageFriends\\'

# For the small scale, we could run it at my own computer 
#out1File = "L:\\Age\\Streams\\sample\\ageUsers-t"+ str(threshold) + "-n" + str(n) + ".txt"
#out2File = "L:\\Age\\Streams\\sample\\label-t"+ str(threshold) + "-n" + str(n) + ".txt"

# For the large scale, we need to run it at the server
out1File = "L:\\Age\\Matlab\\ageUsers-t"+ str(threshold) + "-n" + str(n) + ".txt"
out2File = "L:\\Age\\Matlab\\label-t"+ str(threshold) + "-n" + str(n) + ".txt"
sampleAndLabel(ageFile, out1File, out2File, n)

g = 3
#out1File = "L:\\Age\\Matlab\\equal-ageUsers-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
#out2File = "L:\\Age\\Matlab\\equal-label-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
#equalSample(ageFile, out1File, out2File, g)

from GTStep4Friends import obtainNetwork
# Then we generate the ngrams and the corresponding TF-IDF
nFeatures = 10000

# We first try just 10 friends, because 100 friends of 5000 label users will yield about 15G of feature matrix, which is too huge.
thFriends = 10
#for r in [0, 0.2, 0.5, 0.8, 1]: # The ratio of unigram
for r in [0.5]: # The ratio of unigram
    #out3File = "L:\\Age\\Streams\\sample\\ngram-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + ".txt"
    #out4File = "L:\\Age\\Streams\\sample\\tfidf-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + ".txt"
    
    out3File = "L:\\Age\\Matlab\\ngram-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + ".txt"
    out4File = "L:\\Age\\Matlab\\tfidf-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + ".txt"
    
    #out3File = "L:\\Age\\Matlab\\equal-ngram-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + "-g" + str(g) + ".txt"
    #out4File = "L:\\Age\\Matlab\\equal-tfidf-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + "-g" + str(g) + ".txt"

    findFeatures(refFile, out1File, out3File, nFeatures, r)
    TFIDF(refFile, out1File, out3File, out4File)
    
    # We also obtain the network information
    #out5File = "L:\\Age\\Streams\\sample\\friends-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
    #out6File = "L:\\Age\\Streams\\sample\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
    #out7File = "L:\\Age\\Streams\\sample\\networkFriend-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"

    out5File = "L:\\Age\\Matlab\\friends-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
    out6File = "L:\\Age\\Matlab\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
    out7File = "L:\\Age\\Matlab\\networkFriend-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
    obtainNetwork(out1File, friendFile, followerFile, outFriendsFileRef, out5File, out6File, out7File, thFriends, True)

    #out5File = "L:\\Age\\Matlab\\equal-friends-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
    #out6File = "L:\\Age\\Matlab\\equal-networkLocal-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"
    #out7File = "L:\\Age\\Matlab\\equal-networkFriend-t"+ str(threshold) + "-n" + str(n) + "-g" + str(g) + ".txt"

    #obtainNetwork(out1File, friendFile, followerFile, outFriendsFileRef, out5File, out6File, out7File, thFriends, False)

    #out8File = ("L:\\Age\\Streams\\sample\\ngram-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + 
    #            str(r) + "-f" + str(thFriends) + ".txt")
    #out9File = "L:\\Age\\Streams\\sample\\tfidf-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + \
    #            str(r) + "-f" + str(thFriends) + ".txt"

    #out8File = ("L:\\Age\\Matlab\\ngram-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + 
    #            str(r) + "-f" + str(thFriends) + ".txt")
    #out9File = "L:\\Age\\Matlab\\tfidf-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + \
    #            str(r) + "-f" + str(thFriends) + ".txt"
    out8File = ("L:\\Age\\Matlab\\equal-ngram-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + 
                str(r) + "-f" + str(thFriends) + "-g" + str(g) + ".txt")
    out9File = "L:\\Age\\Matlab\\equal-tfidf-friends-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + \
                str(r) + "-f" + str(thFriends) + "-g" + str(g) + ".txt"
    #TFIDFForFriends(refTweetsDir, out5File, out3File, out8File, out9File)
    
    out10File = "L:\\Age\\Matlab\\weka-tfidf-t"+ str(threshold) + "-n" + str(n) + "-m" + str(nFeatures) + "-r" + str(r) + ".arff"

    #generateForWeka(out4File, out2File, n, nFeatures, out10File)
    #out11File = "L:\\Age\\Matlab\\weka-networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".arff"
    out11File = "L:\\Age\\Matlab\\weka-equal-networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".arff"
    
    #generateByNetworkForWeka(out6File, out2File, out11File)