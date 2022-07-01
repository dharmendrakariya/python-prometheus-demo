# python-prometheus-demo
This repo contains python app with custom metrics and prometheus/grafana stack to monitor the application!


## This repo has two types of approaches for metrics, 1: pull based , 2: push based

## 1: Pull Metrics Based Approach

This is a simple web app demo with a backend and a frontend, in various languages.

## Backend

The backend is available as:

- Python (Flask)
- Go
- Java


## Frontend

The frontend is a PHP application.

## Docker Implementation

To start the application!

```docker-compose up --build -d```

then visit http://localhost:8080 for tha application http://localhost:8000/metrics and for the metrics


To start the monitoring stack!

- go to monitoring folder

```docker-compose up --build -d```

then visit http://localhost:9090 for the prometheus and http://localhost:3000 for the grafana

grafana initia password ```username: admin , password: admin```

importatnt thing is to set the data source

go to settings -> data source -> prometheus

insert value ```http://prometheus:9090```

you can create dashboard using ```dashboard.json```


### Inspiration

https://dev.to/camptocamp-ops/implement-prometheus-metrics-in-a-flask-application-p18


## 2: Push Metrics Based Approach

This requires prometheus push gateway to send the metrics to push gateway and it will send the metrics to Prometheus!

- go to pushgateway-exercise

commands I have executed

```
django-admin startproject testsite

export DJANGO_SETTINGS_MODULE=testsite.settings

```

chnaged allowed hosts in `testsite/settings.py` to "0.0.0.0"

created `metrics.py` and `trybatch.py`

metrics.py creates metrics and trybatch.py is fake job to produce the metrics!

```
pip3.10 install -r requirements.txt

python3.10 metrics.py

python3.10 trybatch.py

```

visit http://localhost:9091 (pushgateway)

there you will be able to see the pushed metrics by trybatch fake job!

then you can visit http:localhost:9090 (prometheus) to check the metrics over there and finally http://localhost:3000 (grafana) to visualize those metrics!

you can create dashboard with the dashboard.json


## Inspiration

https://gist.github.com/codersquid/17f61049c1a817f26da250a4bd2df16d
