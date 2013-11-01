This python script will archive your 3200 most recent tweets (3200 due to api limit) using git.  
The commit date and message will be set to your tweet's while the id is saved in tweet_id to resume archiving later.

This script is forked from [this](https://gist.github.com/2857462).

## Twitter api v1 is dead, oauth is required. Here is how :

1. First create a new application on [dev.twitter.com](https://dev.twitter.com/apps/new)
2. Create config.ini and write your keys
3. Call auth.py and follow instructions to get your oauth tokens. Alternatively you can get them on your app page.  
    auth.py will persist your tokens in config.ini, if you get them from the app page, add them to the file :

```INI
[consumer]
    key    = Your application key
    secret = Application secret
[oauth]
    token  = OAuth token
    secret = secret
```

__That's it, you can now call `python mytweets.py username` to start your archive.__


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/Meroje/twitter-gitarchive/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

