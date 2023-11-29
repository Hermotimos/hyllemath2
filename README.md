# STEPS:

<!-- LOCAL -->
# rename everywhere 'mysite' to the desired project name
# prepare env (requires database setup)
# python -m venv myvenv
# source myvenv\Scripts\activate OR source myvenv/bin/activate OR source myvenv\Scripts\activate
# pip install -r requirements.txt (!! remove stuff for Google Storage if not needed together with mysite.storages.py)

# python manage.py migrate
# python manage.py createsuperuser
# python manage.py makemigrations APPNAME
# python manage.py migrate
# create 'static' and 'media' dir
# python manage.py collectstatic (!! uncomment the right static conf in settings.py)
# python manage.py runserver

<!-- GCP -->
# create GCP project

# create GCP instance or a database in an existing instance (and a user)
# enable Cloud SQL API for the project: https://console.cloud.google.com/apis/library/sqladmin.googleapis.com?project=hyllemath2
# enable Secrets API for the project: https://console.cloud.google.com/apis/enableflow?apiid=secretmanager.googleapis.com&redirect=https:%2F%2Fconsole.cloud.google.com&_ga=2.160338549.973602576.1676100998-1374703551.1676027567&authuser=1&project=hyllemath2

# enter cloud console and: "gcloud config set project PROJECTNAME"
# git clone your repo (!! to the right dir !!)
# enter Code Editor
# create .env in GCP Code Editor and populate it with correct data
<!-- .env, .gitignore etx. are not shown in Code Editor: see them in Terminal with "ls -al" -->

# generate service account key:
    # IAM & Admin -> Service Accounts -> choose Project -> click Email link -> click KEYS tab
    # Add key -> Create new key -> Select JSON as the Key type -> Create
    # https://cloud.google.com/iam/docs/creating-managing-service-account-keys
    # add file gcp-service-account-key.json with the content of the key

# open new Terminal and cd into correct dir
# follow the steps from LOCAL (skip the first step as it should be done with git clone repo)

# in Cloud Shell cd to where manage.py resides and: "gcloud app deploy"




<!-- describe permissions when connecting from project B to project's A db instance - in pA's IAM Admin create principal of the sam name as  B's main service account and grant it with Cloud SQL Client role -->