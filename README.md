# Problem Statement

Given the vast numbers of online buyers, it is difficult for the company to manually go through each and every review and analyse the distribution, find out the major opinion of the buyers, etc. At times, the reviews may be written in foreign languages hence translation is required. Extracting the reviews and displaying a detailed report of the search, translation (if needed) and presenting the analysis report within seconds would save a lot of time. It is also necessary to know the social media influencers at times - their views can influence a large section of buyers. The product developed should address the same.

The scope of the project is to provide a user friendly web based product that would take in the product's name and extract the relevant reviews, analyze it and display a report, based on the search result within seconds. The features of the product would be:

- Display the distribution of the sentiments.

- The polarity is displayed along with the tweet.

- Redirect to the profile, bio, followers, etc of the author on a click.

- See the tweets classified into three sentiments - positive, negative and neutral.

- An option to translate the tweets displayed into any language.

- Display the details of each tweet - timestamp, author, bio, retweets, likes, followers of the author, following.

# Major Functions

## Data Extraction
 
Data is extracted using twitter API and Tweepy. Tweepy is open-sourced, hosted on GitHub and enables Python to communicate with Twitter platform and use its API. Besides tweets, various features related to the tweet are also extracted.

## Sentiment Classification
Tweets are classified into positive, negative and neutral using the model trained and the polarity of each tweet is displayed using textblob.

## Analysis of the extracted data
This is done as per the requirements stated.

## Translation
The entire webpage is translated using google translate API.
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.39.48%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.39.38%20PM.png)


# Snapshots
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.27.19%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.40.11%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.29.56%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.30.07%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.28.26%20PM.png)
![alt text](https://github.com/Himabindugssn/GenuineMetrics/blob/master/Images/Screenshot%202020-11-21%20at%2012.29.13%20PM.png)

