'''
Created on Jun 24, 2015

@author: Jinxue Zhang

We place all the users refine in the third step
'''

'''
Refine the GT users by considering the friendship between the source and the mentioned user
We follow the following steps:
1. We refine the users by the mutual following relationship for the split files
2. We then merge the ageUsers-stream*-refined1.txt and refinedTweets*.txt
3. Only select the users with the tweets >> threshold
4. Manually check the user list and exclude the false ones
'''
import re
def refGTByFriendship(gtF, friendshipF, outputF):
    outf = open(outputF, 'w')
    gtUsers = dict()
    
    # () Matches whatever regular expression is inside the parentheses, and indicates the start and end of a group
    # ?: 0 or 1, need to have a very clear mind to use this symbol
    # [\s|\S]* any character with any length
    # @ is a non-special character
    p = re.compile(r'@[\s|\S]*(can|could) you (please )?(say|tweet|wish|tell|shout)[\s|\S]*happy[\s|\S]*birthday')
    #p = re.compile(r'@[\s|\S]*(can|could) you (please )?(say|tweet|wish|tell|shout)')
    
    for line in open(friendshipF, 'rb'):
        items = line.rstrip('\r\n').split('::')
        if len(items) < 12:
            print line
            continue
        # We also briefly analyze the introduction, and remove the official accounts
        desp = items[-6].lower()
        if "official" not in desp:
            gtUsers[items[0]] = '::'.join(items[-4:])
    for line in open(gtF, 'rb'):
        items = line.rstrip('\r\n').split('::')
        tweet = items[4].lower()
        if re.search(p, tweet):
            continue
        if items[0] in gtUsers:
            friendships = gtUsers[items[0]].split("::")
            if friendships[0] == 'true' and friendships[1] == 'true':
                print >>outf, line.rstrip('\r\n')
            #print >>outf, line.rstrip('\r\n') + "::" + gtUsers[items[0]]
            
        #else:
            #print line
            #print >>outf, line.rstrip('\r\n') + "::false::false::false::false"
    outf.close()

'''
We merge several separate files into one.
For the simplicity, we fix the process of the merging:
First, the ageUsers-stream*-refined1.txt
Second, the refinedTweets*.txt
n: The number of files needs to merge
'''
def mergeFiles(n):
    fdir = 'L:\\Age\\Final\\'
    
    # The first step: merge the ageUsers-stream*-refined1.txt
    import os.path
    resFile = fdir + 'ageUsers-stream-refined1.txt'
    if not os.path.exists(resFile):
        outf = open(resFile, 'w')
        for i in range(1, n + 1):
            inputf = fdir + 'ageUsers-stream'+ str(i) +'-refined1.txt'
            for line in open(inputf, 'rb'):
                print >> outf, line.rstrip('\r\n')
        outf.close()
        print 'Finish the merge of ageUsers-stream*-refined1.txt'

    # The second step: merge the refinedTweets*.txt
    resFile = fdir + 'refinedTweets.txt'
    if not os.path.exists(resFile):
        outf = open(resFile, 'w')
        for i in range(1, n + 1):
            inputf = fdir + 'refinedTweets'+ str(i) +'.txt'
            for line in open(inputf, 'rb'):
                print >> outf, line.rstrip('\r\n')
        outf.close()
        print 'Finish the merge of refinedTweets*.txt'
    
'''
We only consider a user with tweets more than a threshold
We also combine with the refined1 age file
Finally, we will output the refined2 age file by the increasing order of the age
'''    
def chooseUsersWithTweets(refF, outF, outF2, ageF, t):
    userAge = dict()
    userInfo = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        userAge[items[0]] = items[1] + "::" + items[4]
        userInfo[items[0]] = line

    ageUser = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        age = int(items[1])
        user = items[0]
        if age not in ageUser:
            ageUser[age] = set()
        ageUser[age].add(user)
    
    print 'We have users before the tweets limiting:', len(userAge)
    
    outf = open(outF, 'w')
    usersNum = 0
    
    # We remove the repeated users
    chosenUsers = set()
    for line in open(refF, 'rb'):
        if line.startswith("%"):
            if "," not in line:
                user = line.rstrip('\r\n')
                tweets = []
            else:
                #if len(tweets) >= t:
                if len(tweets) >= t and user[1:] in userAge and user[1:] not in chosenUsers:
                    chosenUsers.add(user[1:])
                    usersNum += 1
                    print >> outf, user
                    for tweet in tweets:
                        print >> outf, tweet
                    print >> outf, line.rstrip('\r\n') + '::' + userAge[user[1:]]
        else:
            tweets.append(line.rstrip('\r\n'))
    print 'We have users with ', t, 'tweets :', usersNum
    outf.close()
    
    # Finally we output the refined2 age file
    outf = open(outF2, 'w')
    for age in range(70, 13, -1):
        if age not in ageUser:
            continue
        users = ageUser[age]
        for user in users:
            if user in chosenUsers:
                outf.write(userInfo[user])
                chosenUsers.remove(user)
    outf.close()
    

'''
Sample the tweets for the users by the median value
m: The median value
'''
import random
def sampleTweets(inputF, outputF, m):
    outf = open(outputF, 'w')
    for line in open(inputF, 'rb'):
        if line.startswith("%"):
            if "," not in line:
                user = line.rstrip('\r\n')
                tweets = []
            else:
                myRange = range(len(tweets))
                # Actually, we may no need for the random sample, just the recent tweets?
                if len(tweets) > m:
                    random.shuffle(myRange)
                    
                print >> outf, user
                for i in range(min(len(tweets), m)):
                    print >> outf, tweets[i]
                print >> outf, user, ',', m
        else:
            tweets.append(line.rstrip('\r\n'))
    
'''
Find the distribution of tweets number for each age, and find the median value for the whole user space
'''
import math

def percentile(data, percentile):
    size = len(data)
    return sorted(data)[int(math.ceil((1.0 * size * percentile) / 100)) - 1]

def tweetsDist(refF, ageF):
    # We first build the age-user dictionary
    ageUser = dict()
    for line in open(ageF, 'rb'):
        items = line.split("::")
        age = int(items[1])
        user = items[0]
        if age not in ageUser:
            ageUser[age] = set()
        ageUser[age].add(user)

    # We then find the tweet number for each user
    userTweet = dict()
    for line in open(refF, 'rb'):
        if line[0] == "%" and "," in line:
            items = line.rstrip('\r\n').split(" , ")
            user = items[0][1:]
            if "::" in items[1]:
                userTweet[user] = int(items[1].split('::')[0])
            else:
                userTweet[user] = int(items[1]) 
    ageTweetsWhole = []
    userNumWhole,tweetNumWhole = 0,0
    for age in range(14, 71):
        if age not in ageUser:
            continue
        userNum = len(ageUser[age])
        userNumWhole += userNum
        # In order to output the percentile, we need to maintain a list for each age
        ageTweets = []
        for x in ageUser[age]:
            ageTweets.append(userTweet[x])
            ageTweetsWhole.append(userTweet[x])
        #tweetNum = sum(userTweet[x] for x in ageUser[age])
        tweetNum = sum(ageTweets)
        tweetNumWhole += tweetNum

        print age, userNum, tweetNum, percentile(ageTweets, 10), percentile(ageTweets, 30), \
        percentile(ageTweets, 50), percentile(ageTweets, 70), percentile(ageTweets, 90), 1.0 * tweetNum / userNum
    print userNumWhole, tweetNumWhole, percentile(ageTweetsWhole, 10), percentile(ageTweetsWhole, 30), \
        percentile(ageTweetsWhole, 50), percentile(ageTweetsWhole, 70), percentile(ageTweetsWhole, 90), 1.0 * tweetNumWhole / userNumWhole
        
    return percentile(ageTweetsWhole, 50)

#threshold = 100
#refFile = "L:\\Age\\Streams\\refinedTweets-t"+ str(threshold) + ".txt"
#ageFile = "L:\\Age\\Streams\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt"
#tweetsDist(refFile, ageFile)

'''
Finally, we exclude the users in the suspiciousGT.txt, and generate the final GT file
ageUsers-search-refined3.txt
'''
def excludeSuspicious(gt2F, susF, outF):
    susList = set()
    for line in open(susF, 'rb'):
        items = line.split("::")
        susList.add(items[0])
    outf = open(outF, 'w')
    x = 0
    for line in open(gt2F, 'rb'):
        items = line.split("::")
        if items[0] not in susList:
            outf.write(line)
            x += 1
    outf.close()
    print "We have users after excluding the suspicious users: ", x
   
import os
def mergeRefTweetsFiles():
    fdir = 'L:\\Age\\Final\\friends\\'
    
    inputList = os.listdir(fdir)
    outf = open(fdir + 'Followers-ageUsers-stream.txt', 'w')
    #for ifName in inputList:
    #    #if ifName.endswith('friendships.txt') and ifName.startswith('ageUsers-stream2'):
    #    if ifName.startswith('Friends-ageUsers-stream-'):
    #        print ifName
    #        for line in open(fdir + ifName, 'rb'):
    #            print >> outf, line.rstrip('\r\n')
    for line in open(fdir + 'Followers-ageUsers-stream1.txt', 'rb'):
        print >> outf, line.rstrip('\r\n')
    for line in open(fdir + 'Followers-ageUsers-stream2.txt', 'rb'):
        print >> outf, line.rstrip('\r\n')
    outf.close()
        

#mergeRefTweetsFiles()

''' 
# We first select the users with mutual following relationship
n = 2
for x in range(1, n + 1):
    gtFile = "L:\\Age\\Final\\ageUsers-stream" + str(x) +".txt"
    friendshipFile = "L:\\Age\\Final\\ageUsers-stream" + str(x) +"-friendships.txt"
    outFile = "L:\\Age\\Final\\ageUsers-stream" + str(x) +"-refined1.txt"
    refGTByFriendship(gtFile, friendshipFile, outFile)

    
# We then merge the ageUsers-stream*-refined1.txt and the refinedTweets*.txt 
mergeFiles(n)
'''
    
'''

# In the third step, we choose the users with tweets at least threshold
threshold = 100
tweetFile = "L:\\Age\\Final\\refinedTweets.txt"
refinedTweetsFile = "L:\\Age\\Final\\refinedTweets-t"+ str(threshold) + ".txt"
refinedUser2File = "L:\\Age\\Final\\ageUsers-stream-refined2-t"+ str(threshold) + ".txt"
ageFile = "L:\\Age\\Final\\ageUsers-stream-refined1.txt"
#chooseUsersWithTweets(tweetFile, refinedTweetsFile, refinedUser2File, ageFile, threshold)

# Finally, we manually check and exclude the false ones
refinedUser3File = "L:\\Age\\Final\\ageUsers-stream-refined3-t"+ str(threshold) + ".txt"
susFile = "L:\\Age\\Final\\suspiciousGT.txt"
#excludeSuspicious(refinedUser2File, susFile, refinedUser3File)

#medianValue = tweetsDist(refinedTweetsFile, refinedUser3File)
refinedTweets2File = "L:\\Age\\Final\\refinedTweets-sample-t"+ str(threshold) + ".txt"
#medianValue = 822 for t=100 and 687 for t = 10

# Since the median value of t=100 is larger than t = 10, the number of tweets for t=100 might be larger than t = 10
#sampleTweets(refinedTweetsFile, refinedTweets2File, medianValue)'''