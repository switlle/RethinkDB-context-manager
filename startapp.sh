DIR="/app/wsgi"
cd $DIR
source venv/bin/activate
#export FLASK_APP=restapi.py
#export FLASK_DEBUG=1
#export FLASK_RUN_HOST=0.0.0.0
#export FLASK_RUN_PORT=5000
screen python3.6 api/app.py
