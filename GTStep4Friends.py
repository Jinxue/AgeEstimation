'''
Created on Jul 2, 2015

@author: Jinxue Zhang

Analyze the friends and followers of the network

'''
__all__ = ['obtainNetwork']

'''
We merge several separate files into one.
n: The number of files needs to merge
'''
def mergeFiles(n):
    fdir = 'L:\\Age\\Streams\\friends\\'
    
    # The first step: merge the ageUsers-stream*-refined1.txt
    import os.path
    resFile = fdir + 'Friends-ageUsers-stream.txt'
    if not os.path.exists(resFile):
        outf = open(resFile, 'w')
        for i in range(1, n + 1):
            inputf = fdir + 'Friends-ageUsers-stream'+ str(i) +'.txt'
            for line in open(inputf, 'rb'):
                print >> outf, line.rstrip('\r\n')
        outf.close()
        print 'Finish the merge of Friends-ageUsers-stream*.txt'

    # The second step: merge the refinedTweets*.txt
    resFile = fdir + 'Followers-ageUsers-stream.txt'
    if not os.path.exists(resFile):
        outf = open(resFile, 'w')
        for i in range(1, n + 1):
            inputf = fdir + 'Followers-ageUsers-stream'+ str(i) +'.txt'
            for line in open(inputf, 'rb'):
                print >> outf, line.rstrip('\r\n')
        outf.close()
        print 'Finish the merge of Followers-ageUsers-stream*.txt'

'''
We want to find the local networks of the GT users
Note that we only include the mutual friends
For the first step, we compute the following information:
# friends, # followers, # mutual friends, # local mutual friends
t: the threshold of # mutual friends
'''
def mutualFriends(ageF, friendF, followF, outF, outF2, outF3, t):
    userAge = set()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge.add(items[0])
    
    friends = dict()
    followers = dict()
    
    x = []
    for line in open(friendF, 'rb'):
        if line[0] == '%':
            #if len(x) > 0:
            user = line.split(', ')[0][1:]
            if user in userAge:
                friends[user] = set(x)
            x = []
        else:
            x.append(line.rstrip('\r\n'))
    print len(friends), ' has friends.'

    for line in open(followF, 'rb'):
        if line[0] == '%':
            #if len(x) > 0:
            user = line.split(', ')[0][1:]
            if user in userAge:
                followers[user] = set(x)
            x = []
        else:
            x.append(line.rstrip('\r\n'))
    print len(followers), ' has followers.'

    outf = open(outF, 'w')
    effUsers = set()
    mutFriends = set()
    import random
    for user in userAge:
        m = 0
        if user in friends and user in followers:
            mut = friends[user].intersection(followers[user])
            m = len(mut)
            if m > 0:
                effUsers.add(user)
                if  len(mut) > t:
                    mutFriends |= set(random.sample(mut, t))
                else:
                    mutFriends |=mut
            localM = len(mut.intersection(userAge))
        print >> outf, user, len(friends[user]), len(followers[user]), m, localM
    print len(effUsers), 'Users who have mutual friends. The total mutual friends are', len(mutFriends)
    outf.close()
    
    # Finally we refine the user file
    outf = open(outF2, 'w')
    for line in open(ageF, 'rb'):
        items = line.split("::")
        if items[0] in effUsers:
            print >> outf, line.rstrip('\r\n')
    outf.close()

    outf = open(outF3, 'w')
    for user in mutFriends:
        print >> outf, user
    outf.close()

'''
Build the network information
1. The connections among the label users, representing as a sparse matrix
2. The friends of the label users, representing as a sparse matrix

The key point is to keep consistent of the number of each node. First, we 
number the n label users according to the order in the age file; second, we 
add the mutual friend from n + 1 by the order in the mutual friend file.

For the sampled users, we also sampled the whole friends space. Thus we need to record it also.
****************
Actually we should obtain these two matrixes at the mutualFriends() functions because there is a sampling 
among the mutual friends. However, we have missed it, so just tried to recover 

ageF: the sampled age file
friendF: the whole friends file
followF: the whole followers file
friendsSpaceF: the whole mutual friends space file
outF1: output the corresponding mutual friends according to the ageF
outF2: output the local network information according to the ageF
outF3: output the mutual friends network information according to the ageF
t: the number of mutual friends a label user will select
localFlag: whether we only compute the local network information
'''
def obtainNetwork(ageF, friendF, followF, friendsSpaceF, outF1, outF2, outF3, t, localFlag):
    print "***************Obtaining the network information*********************************"
    userAge = dict()
    userAgeSet = set()
    ind = 1
    for line in open(ageF, 'rb'): 
        items = line.split("::")
        userAge[items[0]] = ind
        userAgeSet.add(items[0])
        ind += 1
    
    friends = dict()
    followers = dict()
    
    x = []
    for line in open(friendF, 'rb'):
        if line[0] == '%':
            #if len(x) > 0:
            user = line.split(', ')[0][1:]
            if user in userAge:
                friends[user] = set(x)
            x = []
        else:
            x.append(line.rstrip('\r\n'))
    print len(friends), ' has friends.'

    for line in open(followF, 'rb'):
        if line[0] == '%':
            #if len(x) > 0:
            user = line.split(', ')[0][1:]
            if user in userAge:
                followers[user] = set(x)
            x = []
        else:
            x.append(line.rstrip('\r\n'))
    print len(friends), ' has followers.'
    
    friendsSpace = set()
    for line in open(friendsSpaceF, 'rb'):
        friendsSpace.add(line.rstrip('\r\n'))
    print 'The whole friends space have ', len(friendsSpace), 'users.'

    chosenFriendsSpace = set()  # We need first record the chosen mutual friends, output it, number it, and then generate the network
    chosenFriendsForEachUser = dict()
    
    outf2 = open(outF2, 'w')
    
    userNum = 0
    import random
    cc = 0
    
    localEdges = set()
    for user in userAge:
        #if user in friends and user in followers:
        mut = friends[user].intersection(followers[user])
        mutFriends = mut.intersection(friendsSpace)
        localFriends = mut.intersection(userAgeSet)

        if  len(mutFriends) > t:
            mutFriends = set(random.sample(mutFriends, t))
            cc += 1

        chosenFriendsSpace |= mutFriends
        chosenFriendsForEachUser[user] = mutFriends

        '''
        Note that since we sampled both the friends and the followers, there might be the case such that
        A is a mutual friend of B, but B has no mutual friend with A. So we need to notice this case.
        '''
        for x in localFriends:
            if x != user:
                localEdges.add(' '.join([str(userAge[user]), str(userAge[x])]))
                localEdges.add(' '.join([str(userAge[x]), str(userAge[user])]))
            #print >> outf2, userAge[user], userAge[x], 1
        
        # We add an I matrix to avoid the singular result
        #print >> outf2, userAge[user], userAge[user], 1
        localEdges.add(' '.join([str(userAge[user]), str(userAge[user])]))
        
        userNum += 1
        if userNum % 1000 == 0:
            print "We have processed ", userNum, 'friends.'
    
    for edge in localEdges:
        print >> outf2, edge, 1
    
    print 'Total Users:' , userNum, 'Total edges:', len(localEdges), 'Edges without self-loop:', len(localEdges) - userNum
    outf2.close()

    if (localFlag):
        return 
    
    outf1 = open(outF1, 'w')
    outf3 = open(outF3, 'w')

    print "We have ", cc, 'users be sampled.'
    print "The friend space after choosing is", len(chosenFriendsSpace)
    
    '''
    One point needs to really care about is the ind.
    We number the label users from 1 to len(ageUser).
    We then continue to number the friends from len(ageUser) + 1 to len(ageUser) + len(friends) + 1
    This setting will impact the constructin of the matrix of the friends later.
    
    ***************************
    Second thought: No need for above consideration because the network is a two-dimentional matrix
    ***************************
    '''
    ind = 1
    chosenFriendsSpaceDict = dict()
    for x in chosenFriendsSpace:
        chosenFriendsSpaceDict[x] = ind
        ind += 1
        print >> outf1, x
    
    for user in userAge:
        mutFriends = chosenFriendsForEachUser[user]
        for x in mutFriends:
            print >> outf3, userAge[user], chosenFriendsSpaceDict[x], 1

    
    outf1.close()
    outf3.close()

'''
Update July 10, 2015
We also exclude the friends with less than t tweets.
Here, the tweets are represented in multiple splited files.
We want to output the refined tweets separately, but combined the refined freinds in a single file. 

******************
Second thought
******************
We might not need to generate the refined tweet files anymore with two reasons:
1. The original file has been refined by excluding the stopping words, etc. Moreover, the tweets are less then 600,
so excluding the users with less than t tweets might not largely reduce the file size.
2. We only need to know the refined friends list.
'''  
import os  
def chooseFriendsWithTweets(refD, outF, friendF, t):
    friends = set()
    for line in open(friendF, 'rb'):
        friends.add(line.rstrip('\r\n'))
    print 'We have', len(friends), 'friends before the tweets limiting.'
    
    # We remove the repeated users
    chosenUsers = set()
    inputList = os.listdir(refD)
    userNum = 0
    for ifName in inputList:
        if not ifName.startswith('ref-CrawlTweets-mutualFriends'):
            continue
        print ifName
        #outf = open(refD + 'ref-' + ifName, 'w')
        for line in open(refD + ifName, 'rb'):
            if line.startswith("%"):
                if "," not in line:
                    user = line.rstrip('\r\n')
                    tweets = []
                else:
                    if len(tweets) >= t and user[1:] in friends and user[1:] not in chosenUsers:
                        chosenUsers.add(user[1:])
                        #print >> outf, user
                        #for tweet in tweets:
                        #    print >> outf, tweet
                        #print >> outf, line.rstrip('\r\n')
                    userNum += 1
                    if userNum % 10000 == 0:
                        print "We have processed ", userNum, 'friends.'
            else:
                tweets.append(line.rstrip('\r\n'))
        #outf.close()
    print 'After refining, we have', len(chosenUsers), 'users with ', t, 'tweets.' 
    
    # Finally we output the refined2 age file
    outf = open(outF, 'w')
    for user in chosenUsers:
        print >> outf, user 
    outf.close()

'''
#mergeFiles(2)

threshold = 100
refFile = "L:\\Age\\Final\\refinedTweets-sample-t"+ str(threshold) + ".txt"
#ageFile = "L:\\Age\\Tweets\\ageUsers-search-refined1.txt"
ageFile = "L:\\Age\\Final\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt"
ageFile2 = "L:\\Age\\Final\\ageUsers-stream-refined4-t"+ str(threshold) + ".txt"

friendFile = "L:\\Age\\Final\\friends\\Friends-ageUsers-stream.txt"
followerFile = "L:\\Age\\Final\\friends\\Followers-ageUsers-stream.txt"

outFile = "L:\\Age\\Final\\network-info.txt"
outFriendsFile = "L:\\Age\\Final\\friends\\mutualFriends.txt"
thFriends = 10
mutualFriends(ageFile, friendFile, followerFile, outFile, ageFile2, outFriendsFile, thFriends)

#chosenFriendsFile = "L:\\Age\\Final\\networkAmongLabel.txt"
#networkLocalFile = "L:\\Age\\Final\\networkAmongLabel.txt"
#networkFriendsFile = "L:\\Age\\Final\\networkFromFriends.txt"
n = 60000
out5File = "L:\\Age\\Streams\\sample\\friends-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
out6File = "L:\\Age\\Streams\\sample\\networkLocal-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"
out7File = "L:\\Age\\Streams\\sample\\networkFriend-t"+ str(threshold) + "-n" + str(n) + "-f" + str(thFriends) + ".txt"

obtainNetwork(ageFile, friendFile, followerFile, outFriendsFile, out5File, out6File, out7File, thFriends, True)

refTweetsDir = 'L:\\Age\\Streams\\friends\\ageFriends\\'
outFriendsFileRef = "L:\\Age\\Streams\\friends\\mutualFriends-refined.txt"

tweetsTh = 100
#chooseFriendsWithTweets(refTweetsDir, outFriendsFileRef, outFriendsFile, tweetsTh)
'''