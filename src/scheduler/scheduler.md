We want to have a scheduler that runs every day to check whether there is an new epsode posted.

More research need to be done on Python Scheduler, but these posts are a good start:
https://devcenter.heroku.com/articles/clock-processes-python
https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flaska

Essentially, we want this scheduler to check whether a new game is added. And there are 
two things we need to check:
  1. Season list: http://j-archive.com/listseasons.php
  2. Game/episode list for lastest season: http://j-archive.com/showseason.php?season=34

Plan A (trashed, see below):
Steps:
1. We record last time when we send the If-Modified-Since request. Write to log.
2. Send new If-Modified-Since request every day. If we receive 304 as response, then it means the nothing
new was added. But if we receive 200 as response, then we should 
  1. update last_time to current timestamp 
  2. if a new season is added:
    1. add season to firebase rn-jeopardy-clues/games/season
  2. go to 3
  3. if a new game is added:
  download, parser and update to firebase. Add to rn-jeopardy-clues/season-<s> and update yyyy-mm-dd to rn-jeopardy-clues/season-<s>/keys
  return True
  4. Write to log

Sadly, since J! Archive server does not return If-Modified-Since (response attached as following), we need plan B.
```
  Date: Sun, 26 Aug 2018 19:48:25 GMT
  Server: Apache/2.2.29 (Unix) mod_ssl/2.2.29 OpenSSL/1.0.1e-fips mod_fcgid/2.3.9 mod_bwlimited/1.4
  X-Powered-By: PHP/5.5.37
  Connection: close
  Transfer-Encoding: chunked
  Content-Type: text/html; charset=utf-8
```

Plan B:
  Similar to the steps in Plan A, but now we are comparing previous md5 and current md5, instead of reponses 
  for If-Modified-Since request. 

ENDPOINTS we need:
  * rn-jeopardy-clues/games/seasons: INT, last_season
  * rn-jeopardy-clues/games/season-<last_season>: list[::-1] is the last episode