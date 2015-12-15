'''
Created on Jun 24, 2015

@author: Jinxue Zhang

We need to preprocessing the tweet corpus, including:
0. Change it to lower case
1. Remove the punctions
2. remove the numbers
3. remove the URLs
4. remove the mentioned users
5. remove the stopping words
6. stemming


We need to process the split files in this process 
'''
import re
from stemming.porter2 import stem
def cleanATweet(tweet, stopWords):
    #tweet = re.sub(r'[^\w\s]', '', corpus)
    #tweet = ' '.join(x.strip() for x in tweet.split())
    
    # We need first remove the http and mentions
    # We may also need to remvoe the hashtags becasue they are not meaningful
    subs = tweet.lower().split()
    items = []   
    for x in subs:
        if "@" not in x and "http" not in x and "#" not in x:
            items.append(x)
    tweet = ' '.join(items)
    
    tweet = re.sub(r'[^a-zA-Z\s]', '', tweet)
    items = []    
    for x in tweet.split():
        #if not x.startswith("http") and not x.startswith("@"):
        keyWord = stem(x.strip())
        if keyWord not in stopWords:
            items.append(keyWord)
    tweet = ' '.join(items)
    return tweet

def preprocessing(inputF, stopWordsF, outF):
    stopWords = set()
    for line in open(stopWordsF, 'r'):
        stopWords.add(line.rstrip('\r\n'))
    print 'We have found', len(stopWords), 'stop words.'
    
    outf = open(outF, 'w')
    lineNum = 0
    for line in open(inputF, 'rb'):
        lineNum += 1
        if lineNum % 1000000 == 0:
            print "We have processed ", lineNum, 'lines'
            
        if line.startswith("%"):
            items = line.split(", ")
            if len(items) == 1:
                print >>outf, line.rstrip('\r\n')
                tweetNum = 0
            else:
                print >> outf, items[0], ',', tweetNum
        #elif not line.startswith("---"):
        
        elif not line.startswith("---"):
            items = line.split('::')
            if len(items) < 16:
                print line
                continue
            #We ignore the retweets
            if items[7].startswith("RT "):
                continue
            tweet = cleanATweet(items[7], stopWords)
            if tweet.rstrip('\r\n') != "":
                tweetNum += 1
                print >> outf, tweet
    outf.close()
'''
We also want to consider the interaction information.

How many interactions are happened with the whole label users, assuming that there is limited 
overlap of different label users' friends.
  
'''
def preprocessingWithInteractions(inputF, outF, userAge):
    
    outf = open(outF, 'w')
    lineNum = 0
    for line in open(inputF, 'rb'):
        lineNum += 1
        if lineNum % 1000000 == 0:
            print "We have processed ", lineNum, 'lines'
            
        if line.startswith("%"):
            items = line.split(", ")
            if len(items) == 1:
                #print >>outf, line.rstrip('\r\n')
                interTweetNum = 0
            else:
                print >> outf, items[0][1:], interTweetNum
        #elif not line.startswith("---"):
        
        elif not line.startswith("---"):
            items = line.split('::')
            if len(items) < 16:
                print line
                continue

            mentions = items[5].split(',')
            for mention in mentions:
                if mention in userAge:
                    interTweetNum += 1
            
    outf.close()

stopWordsFile = "L:\\Age\\Tweets\\stop-word-list.txt"
'''
#inputFile = "L:\\Age\\Streams\\CrawlTweets-ageUsers-stream1-488393175.txt"
inputFile = "L:\\Age\\Streams\\CrawlTweets-ageUsers-stream2-488393181.txt"
outputFile = "L:\\Age\\Streams\\refinedTweets2.txt"
preprocessing(inputFile, stopWordsFile, outputFile)
'''

#ageFile = 'L:\\Age\\Streams\\ageUsers-stream-refined4-t100.txt'
ageFile = 'L:\\Age\\Final\\ageUsers-stream-whole.txt'
userAge = set()
for line in open(ageFile, 'rb'):
    items = line.split("::")
    userAge.add(items[0])

# We process the tweets of the GT user in a folder
import os
fp = 'L:\\Age\\Final\\'
inputList = os.listdir(fp)
for ifName in inputList:
    if not ifName.startswith('CrawlTweets-ageUsers'):
        continue
    print ifName

    # We use the binary mode to avoid the unexpected EOF in the middle of the file
    outputFile = fp + "ref-" + ifName
    preprocessing(fp + ifName, stopWordsFile, outputFile)
        
        

'''
# We process the friends tweets of the GT user
import os
fp = 'G:\\ageFriends\\'
inputList = os.listdir(fp)
for ifName in inputList:
    if not ifName.startswith('CrawlTweets-mutualFriends'):
        continue
    print ifName

    # We use the binary mode to avoid the unexpected EOF in the middle of the file
    #in_f = open(path + '\\Ids\\' + ifName, 'rb')
    b = len('mutualFriends')
    ind = int(ifName.split('-')[1][b:])
    if ind < 25:
    #if ind >= 25 and ind < 49:
    #if ind >= 49:
        #outputFile = 'L:\\Age\\Streams\\friends\\ageFriends\\ref-' + '-'.join(ifName.split('-')[0:2]) + '.txt'
        #preprocessing(fp + ifName, stopWordsFile, outputFile)
        outputFile = 'L:\\Age\\Streams\\friends\\ageFriends\\inter-ref-' + '-'.join(ifName.split('-')[0:2]) + '.txt'
        preprocessingWithInteractions(fp + ifName, outputFile, userAge)
'''        

# We also need to refine the friends by choosing the ones only with more than 100 tweets