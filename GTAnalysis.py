'''
Created on Jun 3, 2015

@author: Jinxue Zhang
Analyze the ground truth about the age
'''
    
'''
In this section, we find the n-grams for each tweet of each user

For each age, we want to output top-K n-grams.
refF: The refined tweets
ageF: the age file
n: n-gram, usually n = 1, 2, 3
K: top-K n-grams for each age

****************
We use the zip builtin to build the n-grams
Zip takes a list of iterables and constructs a new list of tuples 
where the first list contains the first elements of the inputs, 
the second list contains the second elements of the inputs, and so on. 

**********************************************************************
Update 24 June, 2015,
Changed the ngrams building from zip method to the string method, reduce the memory to half and the speed to 20X less.
The reason is that the zip method generates the list while the method yields the string, which will be used as the key later.
'''
__all__ = ['find_ngrams', 'ngrams_stats_init_by_age_repeat', 'ngrams_stats_init_by_age_wo_repeat', \
           'ngrams_stats_init_by_user_wo_repeat', \
           'getTopKngrams', 'getTopKngramsDist', 'getOneNgramDist', \
           'TFIDF', 'TFIDFForFriends']

def find_ngrams(input_list, n):
    #return zip(*[input_list[i:] for i in range(n)])
    res = []
    L = len(input_list)
    if L < n:
        return res
    for i in range(L - n + 1):
        res.append(" ".join(input_list[i:(i + n)]))
    return res

'''
We aggregate the ngrams by age. For each ngram showing multiple times for a single user, we will count the appearance times.
'''
def ngrams_stats_init_by_age_repeat(refF, ageF, n):
    # We first build the user-age dictionary
    userAge = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = int(items[1])
    
    # We then build a dictionary for each age
    ageNGram = dict()
    for age in range(14, 71):
        ageNGram[age] = dict()
    
    # We then check the tweets
    userNum = 0
    for line in open(refF, 'rb'):
        if line[0] == "%" and "," not in line:
            userNum += 1
            if userNum % 1000 == 0:
                print "We have processed ", userNum, 'users.'
            user = line.rstrip('\r\n')[1:]
            age = userAge[user]
            ngram = ageNGram[age]
        elif line[0] != "%":
            for gram in find_ngrams(line.split(), n):
                if gram in ngram:
                    ngram[gram] += 1
                else:
                    ngram[gram] = 1
    
    print "Finish the ngram building."
    return ageNGram

'''
In this method, we aggregate the repeated ngrams for each user, and group them by age.
'''
def ngrams_stats_init_by_age_wo_repeat(refF, ageF, n):
    # We first build the user-age dictionary
    userAge = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = int(items[1])
        
    ageUser = dict()
    # We then build a dictionary for each age
    ageNGram = dict()
    for age in range(14, 71):
        ageNGram[age] = dict()
        ageUser[age] = set()
    
    # We then check the tweets
    userNum = 0
    
    #The change at 22 June 2015. We only choose the users who are in the age file by adding the 'chosen' variable.
    chosen = False
    for line in open(refF, 'rb'):
        if line[0] == "%":
            if "," not in line:
                user = line.rstrip('\r\n')[1:]
                if user in userAge:
                    chosen = True
                else:
                    chosen = False
                    continue
                age = userAge[user]
                ngramAge = ageNGram[age]
                ngram = set()   # We create a new set to record the ngram for this user
            elif chosen == True:
                userNum += 1
                if userNum % 1000 == 0:
                    print "We have processed ", userNum, 'users.'

                # We then merge the ngram of this user to the whole ngram dict
                for gram in ngram:
                    if gram in ngramAge:
                        ngramAge[gram] += 1
                    else:
                        ngramAge[gram] = 1
                if len(ngram) > 0:
                    ageUser[age].add(user)
                
        elif chosen == True:
            for gram in find_ngrams(line.split(), n):
                ngram.add(gram)
    
    print "Finish the ngram building for ngram = ", n
    return ageNGram, ageUser

'''
In this method, we need to generate all the ngrames for each user. We don't consider the repeated ngrams for each user.
**** May be not necessary. We could directly build the TF-IDF matrix as follows.
'''
def ngrams_stats_init_by_user_wo_repeat(refF, ageF, n):
    # We first build the user-age dictionary
    userAge = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = int(items[1])
        
    ageUser = dict()
    # We then build a dictionary for each age
    userNGram = dict()
    
    # We then check the tweets
    userNum = 0
    
    #The change at 22 June 2015. We only choose the users who are in the age file by adding the 'chosen' variable.
    chosen = False
    for line in open(refF, 'rb'):
        if line[0] == "%":
            if "," not in line:
                user = line.rstrip('\r\n')[1:]
                if user in userAge:
                    chosen = True
                else:
                    chosen = False
                    continue
                age = userAge[user]
                ngram = set()   # We create a new set to record the ngram for this user
            elif chosen == True:
                userNum += 1
                if userNum % 1000 == 0:
                    print "We have processed ", userNum, 'users.'
                    
                # We then merge the ngram of this user to the whole ngram dict
                userNGram[user] = ngram
                if len(ngram) > 0:
                    ageUser[age].add(user)
                
        elif chosen == True:
            for gram in find_ngrams(line.split(), n):
                ngram.add(gram)
    
    print "Finish the ngram building for ngram = ", n
    return userNGram, ageUser


'''
Given the ngrams, we could build the TF-IDF directly.
'''
import math
def TFIDF(refF, ageF, featureF, outF):
    print "***************Starting the TF-IDF building*********************************"
    # We first build the user-age dictionary
    userAge = dict()
    #userAge_ordered = []
    ind = 1
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = ind
        #userAge_ordered.append(items[0])
        ind += 1
    print 'We have', len(userAge), 'users.'

    chosenNGs = dict()
    #chosenNGs_ordered = [] 
    chosenNGs_order = dict()
    ind = 1
    for line in open(featureF, 'rb'):
        items = line.rstrip('\r\n').split()
        ng = ' '.join(items[0:-1])
        chosenNGs[ng] = int(items[-1])
        #chosenNGs_ordered.append(ng)
        chosenNGs_order[ng] = ind
        ind += 1
    print 'We have', len(chosenNGs), 'features.'
    
    # We then build a dictionary for each age
    userNGram = dict()
    
    # We also record the number of users have the chosen ngrams, which representing IDF
    #idf = dict()
    
    # We then check the tweets
    userNum = 0
    
    #The change at 22 June 2015. We only choose the users who are in the age file by adding the 'chosen' variable.
    chosen = False
    for line in open(refF, 'rb'):
        if line[0] == "%":
            if "," not in line:
                user = line.rstrip('\r\n')[1:]
                if user in userAge:
                    chosen = True
                else:
                    chosen = False
                    continue
                ngram = dict()   # We create a new dict to record the ngram for this user
            elif chosen == True:
                userNum += 1
                if userNum % 1000 == 0:
                    print "We have processed ", userNum, 'users.'
                    
                # We then merge the ngram of this user to the whole ngram dict
                userNGram[user] = ngram
                #for ng in ngram:
                #    if ng not in idf:
                #        idf[ng] = 0
                #    idf[ng] += 1
                
        elif chosen == True:
            # We will consider unigram and digrams
            for gram in find_ngrams(line.split(), 1):
                if gram in chosenNGs:
                    if gram not in ngram:
                        ngram[gram] = 0
                    ngram[gram] += 1
            for gram in find_ngrams(line.split(), 2):
                if gram in chosenNGs:
                    if gram not in ngram:
                        ngram[gram] = 0
                    ngram[gram] += 1
                    
    print "Finish the TF and IDF building."

    '''
    UPDATE July 8, 2015:
    There is a big bug when building the TF-IDF matrix. Previously we built the label matrix by the descending ages.
    However, here we use a dictionary constructed from the age file to build the TF-IDF matrix. Since the key order will 
    change in the dictionary and be different with the inserting order, these two matrixes are inconsistent. Actually,
    the order in the dictionary is totally random. Therefore, the accuracy is always about 50%. 
    
    Moreover, we could store the file as a sparse matrix format, with (i, j, value) in each line
    '''
    
    '''
    # Store the TF-IDF as the normal matrix
    outf = open(outF, 'w')
    N = len(userAge)
    userNum = 0
    #for user in userAge:
    for i in range(N):
        user = userAge_ordered[i]
        tfidf = []
        if user not in userNGram:
            print user
            continue
        ngram = userNGram[user]
        #for t in idf:
        #    if t in ngram and idf[t] > 0:
        #        x = ngram[t] * math.log(1.0 * N / idf[t])
        #for t in chosenNGs:
        for j in range(len(chosenNGs_ordered)):
            t = chosenNGs_ordered[j]
            if t in ngram and chosenNGs[t] > 0:
                x = ngram[t] * math.log(1.0 * N / chosenNGs[t])
                tfidf.append(x)
            else:
                tfidf.append(0)
        print >> outf, ' '.join(str(x) for x in tfidf)
        userNum += 1
        if userNum % 1000 == 0:
            print "We have output ", userNum, 'users\' TF-IDF.'
    '''
    
    '''
    We could also store the TF-IDF as the sparse matrix.
    Because the matrix is represented with the format of sparse matrix, we could randomly write the edges, 
    instead of following the order of users and features.
    '''
    outf = open(outF, 'w')
    N = len(userAge)
    userNum = 0
    #for user in userAge:
    for user in userNGram:
        ngram = userNGram[user]
        
        if len(ngram) == 0:
            continue
        #maxF = max(ngram.values())
        #for t in idf:
        #    if t in ngram and idf[t] > 0:
        #        x = ngram[t] * math.log(1.0 * N / idf[t])
        for t in ngram:
            if chosenNGs[t] > 0:
                # This is the basic TF-IDF computation method
                x = ngram[t] * math.log(1.0 * N / chosenNGs[t])
                '''We could also try the TF with augmented frequency, to prevent a bias towards longer documents, 
                e.g. raw frequency divided by the maximum raw frequency of any term in the document.
                Moreover, we could try the IDF with smoothing by adding 1 in the log function
                '''
                #x = (0.5 + 0.5 * ngram[t] / maxF) * math.log(1 + 1.0 * N / chosenNGs[t])
                #x = (0.5 + 0.5 * ngram[t] / maxF) * math.log(1.0 * N / chosenNGs[t])
                print >> outf, userAge[user], chosenNGs_order[t], x
                #tfidf.append(x)
            #else:
                #tfidf.append(0)
        #print >> outf, ' '.join(str(x) for x in tfidf)
        userNum += 1
        if userNum % 1000 == 0:
            print "We have output", userNum, 'users\' TF-IDF.'
        

    outf.close()

'''
We need to build a different version of TF-IDF method for the friends.
The difference from the above one are:
1. The ngram is fixed, the how many users use this ngram is not decided not in the file
2. The refined corpus is composed by multiple files

Since it is not feasible to load all the ngrams of the whole friends space into the memory, we just use a simplified 
TF-IDF. We compute the TF-IDF for each file in the folder. Before that, we need to go through the whole corpus to obtain
how many users use this ngram (IDF).  

***********
Note that some friends may have zero tweet, we just let the corresponding feature vector be zero.
***********

refD: The folder for the refined tweets files
freindF: The sampled friend file
featureF: The feature file generated from the label data
outF1: the feature file for the friends
outF2: the sparse matrix for the TF-IDF of the friends 
''' 
def TFIDFForFriends(refD, friendF, featureF, outF1, outF2):

    # We first build the user-age dictionary.
    ind = 1
    friends = set()
    friends_ordered = dict()
    for line in open(friendF, 'rb'):
        friends.add(line.rstrip('\r\n'))
        friends_ordered[line.rstrip('\r\n')] = ind
        ind += 1
    print 'We have', len(friends), 'friends.'

    # We then scan the whole tweets folder and find how many users use a specific ngram
    chosenNGs = dict() # Record the IDF value for this ngram
    chosenNGs_ordered = [] # A list with the adding order
    chosenNGs_order = dict()    # record the ind number for each ngram 
    import os.path
    ind = 1
    if os.path.exists(outF1):
        for line in open(outF1, 'rb'):
            items = line.rstrip('\r\n').split()
            ng = ' '.join(items[0:-1])
            chosenNGs[ng] = int(items[-1])
            chosenNGs_ordered.append(ng)
            chosenNGs_order[ng] = ind
            ind += 1
    else:
        for line in open(featureF, 'rb'):
            items = line.rstrip('\r\n').split()
            ng = ' '.join(items[0:-1])
            chosenNGs[ng] = 0
            chosenNGs_ordered.append(ng)
            chosenNGs_order[ng] = ind
            ind += 1
        print 'We have', len(chosenNGs), 'features.'
    
        inputList = os.listdir(refD)
        userNum = 0
        for ifName in inputList:
            if not ifName.startswith('ref-CrawlTweets-mutualFriends'):
                continue
            print ifName
            for line in open(refD + ifName, 'r'):
                if line[0] == "%":
                    if "," not in line:
                        user = line.rstrip('\r\n')[1:]
                        if user in friends:
                            chosen = True
                        else:
                            chosen = False
                            continue
                        ngram = set()   # We create a new dict to record the ngram for this user
                    elif chosen == True:
                        userNum += 1
                        if userNum % 10000 == 0:
                            print "We have processed ", userNum, 'friends.'
                            
                        # We then merge the ngram of this user to the whole ngram dict
                        for ng in ngram:
                            chosenNGs[ng] += 1
                elif chosen == True:
                    # We will consider unigram and digrams
                    for gram in find_ngrams(line.split(), 1):
                        if gram in chosenNGs:
                            ngram.add(gram)
                    for gram in find_ngrams(line.split(), 2):
                        if gram in chosenNGs:
                            ngram.add(gram)
        
        print 'Finish the IDF building for the friends.'
        
        # We then output the feature IDF for the friends
        outf = open(outF1, 'w')
        for ng in chosenNGs_ordered:
            print >> outf, ng, chosenNGs[ng]
        outf.close() 

    userNum = 0
    chosen = False
    # Then we compute the TF for each file

    outf = open(outF2, 'w')
    inputList = os.listdir(refD)
    for ifName in inputList:
        if not ifName.startswith('ref-CrawlTweets-mutualFriends'):
            continue
        print ifName
        
        # We first build a dictionary for each age
        userNGram = dict()
        for line in open(refD + ifName, 'r'):
            if line[0] == "%":
                if "," not in line:
                    user = line.rstrip('\r\n')[1:]
                    if user in friends:
                        chosen = True
                    else:
                        chosen = False
                        continue
                    ngram = dict()   # We create a new dict to record the ngram for this user
                elif chosen == True:
                    userNum += 1
                    if userNum % 10000 == 0:
                        print "We have compute the TF for ", userNum, 'users.'
                        
                    # We then merge the ngram of this user to the whole ngram dict
                    userNGram[user] = ngram
                    
            elif chosen == True:
                # We will consider unigram and digrams
                for gram in find_ngrams(line.split(), 1):
                    if gram in chosenNGs:
                        if gram not in ngram:
                            ngram[gram] = 0
                        ngram[gram] += 1
                for gram in find_ngrams(line.split(), 2):
                    if gram in chosenNGs:
                        if gram not in ngram:
                            ngram[gram] = 0
                        ngram[gram] += 1
                    
        #print "Finish the TF and IDF building for this file."
        
        # We could also store the TF-IDF as the sparse matrix
        '''
        Our idea here is to record the TF-IDF of user in each file separately.
        Because the matrix is represented with the format of sparse matrix, we could randomly write the edges, 
        instead of following the order of users and features.
        '''
        N = len(friends)
        #for user in userAge:
        for user in userNGram:
            ngram = userNGram[user]
            
            if len(ngram) == 0:
                continue
            maxF = max(ngram.values())

            for t in ngram:
                if chosenNGs[t] > 0:
                    # This is the basic TF-IDF computation method
                    #x = ngram[t] * math.log(1.0 * N / chosenNGs[t])
                    '''We could also try the TF with augmented frequency, to prevent a bias towards longer documents, 
                    e.g. raw frequency divided by the maximum raw frequency of any term in the document.
                    Moreover, we could try the IDF with smoothing by adding 1 in the log function
                    '''
                    #x = (0.5 + 0.5 * ngram[t] / maxF) * math.log(1 + 1.0 * N / chosenNGs[t])
                    x = (0.5 + 0.5 * ngram[t] / maxF) * math.log(1.0 * N / chosenNGs[t])
                    print >> outf, friends_ordered[user], chosenNGs_order[t], x
                    #tfidf.append(x)
                #else:
                    #tfidf.append(0)
            #print >> outf, ' '.join(str(x) for x in tfidf)

    outf.close()
    
'''
Output the top-K
'''
def getTopKngrams(outF, ageNGram, K):    
    # Finally we output the top-K list for each age
    outf = open(outF, 'w')
    for age in range(14, 71):
        ngram = ageNGram[age]
        total = sum(ngram.values())
        ngramNum = len(ngram)
        ordered = sorted(ngram.items(), key=lambda x: x[1], reverse=True)
        out_str = []
        for k in range(min(K, len(ordered))):
            out_str.append(ordered[k])
        print age, total, out_str
        print >> outf, str(age)  + "::" + str(ngramNum) + "::" + str(total) + "::" + str(out_str)
    outf.close()
    
'''We also compute the distribution of each ngram in the whole age range. 
Specifically, we compute the distribution of each top-10 ngram for each age.

ageNGram: The dictionary for the ngrams at each age
ageUser: the age - user dictionary
K: top K list
'''
def getTopKngramsDist(outF, ageNGram, ageUser, K): 
    outf = open(outF, 'w')
    for age in range(14, 71):
        # First we output the top-K ngrams
        ngram = ageNGram[age]           # The ngram dictionary for this specific age
        userNum = len(ageUser[age])     # The number of users in this age group
        total = sum(ngram.values())     # The sum of appearances for the whole ngrams (repeated)
        ngramNum = len(ngram)           # The number of ngrams for this age group
        ordered = sorted(ngram.items(), key=lambda x: x[1], reverse=True)
        out_str = []
        for k in range(min(K, len(ordered))):
            out_str.append(ordered[k])
        print age, userNum, ngramNum, total, out_str
        print >> outf, str(age)  + "::" + str(userNum) + "::"   + str(ngramNum) + "::" + str(total) + "::" + str(out_str)
        
        # Then we output the distribution for each top ngram
        for k in range(min(K, len(ordered))):
            keyNgram = ordered[k][0]
            ratioList = []
            for otherAge in range(14, 71):
                otherNgram = ageNGram[otherAge]
                #total = sum(otherNgram.values())
                total = len(ageUser[otherAge])
                ratio = 0.0
                if keyNgram in otherNgram:
                    ratio = 1.0 * otherNgram[keyNgram] / total
                ratioList.append(ratio)    
            #print keyNgram, ratioList
            print >> outf, "%", keyNgram
            print >> outf, ratioList
        
'''refFile = "L:\\Age\\Tweets\\refinedTweets-t"+ str(threshold) + ".txt"
#ageFile = "L:\\Age\\Tweets\\ageUsers-search-refined1.txt"
ageFile = "L:\\Age\\Tweets\\ageUsers-search-refined3-t"+ str(threshold) + ".txt"
K = 10
#n = 1
for n in range(1, 4): 
    outFile = "L:\\Age\\Tweets\\ngrams-" + str(n) + "-user-t"+ str(threshold) + ".txt"
    #ageNGram = ngrams_stats_init(refFile, ageFile, n)
    ageNGram, ageUser = ngrams_stats_init_user(refFile, ageFile, n)
    #getTopKngrams(outFile, ageNGram, K) 
    getTopKngramsDist(outFile, ageNGram, ageUser, K)
'''      
            
 
        
'''
Given a ngram, we compute the distribution on each age

ageNGram: The dictionary for the ngrams at each age
ageUser: the age - user dictionary
ng: The input ngram, with the format of tuple
'''
def getOneNgramDist(ageNGram, ageUser, ng): 
    ratioList = []
    numList = []
    for age in range(14, 71):
        # First we output the top-K ngrams
        ngram = ageNGram[age]
        userNum = len(ageUser[age])
        
        ratio = 0.0
        num = 0
        if ng in ngram:
            ratio = 1.0 * ngram[ng] / userNum
            num = ngram[ng]
        ratioList.append(ratio)
        numList.append(num)
    #print ng, ratioList
    #print ng, ["%0.2f" % f for f in ratioList]
    print "%", ng
    print '[', ", ".join("%.2f" % f for f in ratioList), ']' 
    #print '[', ", ".join("%.2f" % f for f in numList), ']' 

'''
Obtain the tweets for each user set 
'''
def obtainTweets(refF, ageF):
    # We first build the user-age dictionary
    userAge = set()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge.add(items[0])

    print 'Users', len(userAge)
    chosen = False
    tweets = 0
    userNum = 0
    for line in open(refF, 'rb'):
        if line[0] == "%":
            if "," not in line:
                user = line.rstrip('\r\n')[1:]
                if user in userAge:
                    chosen = True
                else:
                    chosen = False
                    continue
            elif chosen == True:
                #print line
                userNum += 1
                if userNum % 1000 == 0:
                    print "We have processed ", userNum, 'users.'
                # Format : 
                #%41348705 , 2119::21::Happy 21st Birthday to my favorite tatted wild child @Zack_Hillis82  hope you're still alive to see this ??

                tweets += int(line.split(' , ')[1].split('::')[0])
                # We then merge the ngram of this user to the whole ngram dict
                
                #for ng in ngram:
                #    if ng not in idf:
                #        idf[ng] = 0
                #    idf[ng] += 1       
    print 'has Tweets', tweets

'''
threshold = 100
refFile = "L:\\Age\\Final\\refinedTweets-sample-t"+ str(threshold) + ".txt"
#ageFile = "L:\\Age\\Tweets\\ageUsers-search-refined1.txt"
ageFile = "L:\\Age\\Final\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt"

#ngList = [('support',),('run',), ('home',), ('book',), ('hate',), \
#          ('high','school'),('hard', 'work'),('pretti', 'sure'),('ice', 'cream'),('day', 'work')]
#ngList = ['support', 'run', 'home', 'book', 'hate', \
#          'high school', 'hard work', 'pretti sure', 'ice cream', 'day work']
ngList = ['look forward', 'good luck', 'thank god']
preN = 0
for ng in ngList:
    if preN != len(ng.split()):
        preN = len(ng.split())
        totalUsers = 0
        ageNGram = dict()
        ageUser = dict()
        ageNGram, ageUser = ngrams_stats_init_by_age_wo_repeat(refFile, ageFile, preN)
        for x in ageUser:
            totalUsers += len(ageUser[x])
            print x, len(ageUser[x])
        print 'Total users:', totalUsers
    getOneNgramDist(ageNGram, ageUser, ng)'''

#obtainTweets("L:\\Age\\Final\\refinedTweets-t100.txt", "L:\\Age\\Matlab\\ageUsers-t100-n60000.txt")
obtainTweets("L:\\Age\\Final\\refinedTweets-t100.txt", "L:\\Age\\Matlab\\equal-ageUsers-n60000-t100-g3.txt")