# jeopardy-spider
Python spider for jeopardy games on [J! Archive](http://j-archive.com/). This library provide 2 options: a spider monitoring and uploading newly added Jeopardy episodes in [heroku_scheduler](./src/heroku_scheduler.py) and a crawler with gevent for scraping and uploading a season of Jeopardy games in [run](./src/run.py). 

## Setup

```bash
git clone https://github.com/n33t1/jeopardy-parser.git
cd jeopardy-spider
pip install -r requirements.txt
```

Then you will need to set up firebase, download admin keys and store them in `./keys/rn-jeopardy-admin-keys.json` in order to use Firebase database.

### Heroku Setup

`heroku cli` is required for deploying the spider to heroku. ([Download link and guide here](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)). The following guide assumes you have installed the cli and have run `heroku login` with your heroku credentials.

```bash
git clone https://github.com/n33t1/jeopardy-spider.git
cd jeopardy-spider
heroku create # create a dyno
heroku rename rn-jeopardy-spider-2 # (Optional) Rename the dyno
heroku config:set CONFIG_VARIABLE_NAME=VALUE # Set config variables for heroku dyno, more details below
git push heroku master # Deploys the spider
```

After deployment, the project will check for new seasons and episodes every day using heroku's `clock` worker. There is no web entrypoint, and logs can be obtained by `heroku logs --tail`

#### Config Variables

This project stores the credentials of firebase admin SDK using heroku's config variables. The names of the config vars in use in `database/service_credentials.py` are as follows:
|Name in Heroku|Firebase Admin SDK Credentials Field|
|:-------------------------:|:---------------------:|
|`CERT-PROJECT-ID`          |`project_id`           |
|`CERT-PRIVATE-KEY-ID`      |`private_key_id`       |
|`CERT-PRIVATE-KEY`         |`private_key`          |
|`CERT-CLIENT-EMAIL`        |`client_email`         |
|`CERT-CLIENT-ID`           |`client_id`            |
|`CERT-CLIENT-X509-CERT-URL`|`client_x509_cert_url` |

Create the config vars using `heroku config:set NAME:VALUE` for the remote dyno. For testing heroku locally using `heroku local`, run `heroku config:get -s > ./.env` at project root so the variables are available to the program.

## Example

Examples use of crawling Jeopardy games by season:

```bash
python src/run.py -s 34 -d # delete season 34 from firebase DB
python src/run.py -s 34 -u # upload season 34 to firebase DB
```

## TODO

Some fancy AI/NLP stuff we can do:
  1. Better Roman Numerals detection and smarter parsing for answers. Something to detect the semantic meaning.  
  2. Classification over `What if` and `Who is`.
