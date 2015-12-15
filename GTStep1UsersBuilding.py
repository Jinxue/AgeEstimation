'''
Created on Jun 2, 2015

@author: Jinxue Zhang

*****************************************************************************************
This is the first step to find the ground truth users from the search/stream files. 
After finishing this first step, we need to crawl the tweets for the further process.
*****************************************************************************************

 * From the tweets with the "happy xx birthday", we build the ground truth based on two conditions:
 * 1. Exactly the words of "happy xx birthday",  for example, 20th, 21st, 22nd, 23rd, etc
 * 2. The tweet only mentions one person
 
For the ageTweets-Steam.txt
Each line is a tweet with 16 items and formed as:
status_ID::ReplyInStatusID::ReplyInUserID::RetweetCount::RetweetInStatusID::MentionEnt::
URLEnt::Text::Time::App::geocode::userID::screenName::userName::ReadableTime::mediaURl

For the ageTweets-Search.txt
Each line is a tweet with 16 items and formed as:
Age::status_ID::ReplyInStatusID::ReplyInUserID::RetweetCount::RetweetInStatusID::MentionEnt::
URLEnt::Text::Time::App::geocode::userID::screenName::userName::ReadableTime
We add a age item in the beginning, but without the mediaURL at the end

'''

from sets import Set

def oneBuilding(inputF, outputF):
    outf = open(outputF, 'w')
    # For each user, we only let him endorse one person
    userSet = Set()
    ageUserSet = Set()
    
    # We first build a key word list
    keyWords = dict()
    for i in range(13, 71):
        keyWord = ""
        if i % 10 == 1:
            keyWord = "happy " + str(i) + "st birthday"
        elif i % 10 == 2:
            keyWord = "happy " + str(i) + "nd birthday"
        elif i % 10 == 3:
            keyWord = "happy " + str(i) + "rd birthday"
        else:
            keyWord = "happy " + str(i) + "th birthday"
        keyWords[keyWord] = i
    
    for line in open(inputF, 'rb'):
        items = line.rstrip('\r\n').split('::')
        if len(items) < 16:
            #print line
            continue
        
        # We first need to handle two types of files
        posOff = 0
        if "search" in inputF.lower():
            posOff = 1
    
        tweet = items[7 + posOff]
        tweetId = items[posOff]
        userFriendName = items[posOff -4]
        dateTime = items[- 2 + posOff]
        if userFriendName in userSet:
            #print line
            continue
        else:
            userSet.add(userFriendName)
    
        # Ignore the retweets
        if items[4 + posOff] != "-1" or 'RT ' in tweet:
                continue
    
        # If there was no mention we skip
        if items[5 + posOff] == "-1":
                continue
        else:
            mentionComb = items[5 + posOff].split(',')
            if len(mentionComb) != 2:
                continue
            else:
                AgeUser = mentionComb[-1]
            AgeUser = mentionComb[-1]
        if AgeUser in ageUserSet:
            print line
            continue
        else:
            ageUserSet.add(AgeUser)
            
        for keyWord in keyWords.keys():
            if keyWord in tweet.lower():
                # user, age, tweetId, user's friend, tweet, time
                print >> outf, AgeUser + "::" + str(keyWords[keyWord]) + "::" + tweetId + "::" + userFriendName + "::" + tweet + "::" + dateTime
    outf.close()
    
    
def distAmongAge(inputF):
    distAge = dict()
    totalUsers = 0
    for line in open(inputF, 'rb'):
        items = line.split('::')
        if items[1] in distAge:
            distAge[items[1]] += 1
        else:
            distAge[items[1]] = 1
        totalUsers += 1
    ordered = sorted(distAge.items(), key=lambda x: x[0], reverse=False)
    for age, cnt in ordered:
        print age, cnt, 1.0 * cnt / totalUsers

    
#inputFile = "L:\\Age\\ageTweets-Stream.txt"
#outputFile = "L:\\Age\\ageUsers-stream-notOneMention.txt"
#outputFile = "L:\\Age\\ageUsers-stream.txt"
#oneBuilding(inputFile, outputFile)
#distAmongAge(outputFile)

#inputFile = "L:\\Age\\ageTweets-Search.txt"
#outputFile = "L:\\Age\\ageUsers-search-notOneMention.txt"
outputFile = "L:\\Age\\Final\\ageUsers-stream-refined4-t100.txt"
#oneBuilding(inputFile, outputFile)
distAmongAge(outputFile)

#distAmongAge(outFile)