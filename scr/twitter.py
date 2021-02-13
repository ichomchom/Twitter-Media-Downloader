import tweepy
import csv
from urllib.request import urlopen
import os
import requests
import youtube_dl



# Twitter API credentials

consumer_key = 'your_twitter_consumer_key'
consumer_secret = 'your_twitter_consumer_secret'
access_key = 'your_twitter_access_key'
access_secret = 'your_twitter_access_secret'


# initialize a list to hold all the tweepy Tweets

def redirect(url):
    page = urlopen(url)
    return page.geturl()


def get_all_tweets(screen_name, userDir):

     # Twitter only allows access to a users most recent 3240 tweets with this method

     # authorize twitter, initialize tweepy

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

     # initialize a list to hold all the tweepy Tweets

    alltweets = []

     # make initial request for most recent tweets (200 is the maximum allowed count)

    try:
      new_tweets = api.user_timeline(screen_name=screen_name, count=1,
                                    tweet_mode='extended',
                                    include_entities=True)
    except Exception:
      print('[LOG] deleted account')
      return

     # save most recent tweets

    alltweets.extend(new_tweets)

     # save the id of the oldest tweet less one
    if len(alltweets) == 0:
      return
    else:
      oldest = alltweets[-1].id - 1

     # keep grabbing tweets until there are no tweets left to grab

    while len(new_tweets) > 0:

          # all subsequent requests use the max_id param to prevent duplicates

        new_tweets = api.user_timeline(screen_name=screen_name,
                count=200, max_id=oldest, tweet_mode='extended',
                include_entities=True)

          # save most recent tweets

        alltweets.extend(new_tweets)

          # update the id of the oldest tweet less one

        oldest = alltweets[-1].id - 1

    outtweets = []  # initialize master list to hold our ready tweets
    ydl_opts = {
          'outtmpl': userDir + '%(extractor)s-%(id)s-%(title)s.%(ext)s',
          'format': 'bestaudio/best'
      }
    for tweet in alltweets:
        if tweet.entities.get('media') is not None:
            pic = tweet.entities['media'][0]['media_url']
            if 'thumb' in pic:
              try:
                vid = tweet.extended_entities['media'][0]['video_info']['variants'][0]['url']
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                  try:
                    ydl.download([vid])
                  except youtube_dl.utils.DownloadError as e:
                    print(e)
                  except Exception as ex:
                    pritn(ex)
              except KeyError:
                print('[LOG] No Video')
            else:
              r = requests.get(pic)
              if not os.path.exists(userDir + pic.split('/')[4]):
                try:
                  with open(userDir + pic.split('/')[4], "wb") as file:  
                  # Use requests to download image
                    file.write(r.content) 
                    print('[LOG] Done Getting ' + pic)
                except IsADirectoryError as e:
                  print('No Folder')
                except OSError as e:
                  print(e)
                except Exception as ex:
                  print(ex)
                
if __name__ == '__main__':
    dir = \
        r'your/directory'

  # pass in the username of the account you want to download

    with open('./usernames.txt') as f:
        usernames = f.read().splitlines()

  # create directory for each username
    for user in usernames:
      try:
        userDir = dir + user + '/'
        os.mkdir(userDir)
      except OSError:
        print(dir + user + ' already created.')
        pass
      else:
        print(dir + user + ' successfully created.')
      get_all_tweets(user, userDir)
    
    print('[LOG] Done')
    

