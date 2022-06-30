# python-prometheus-demo
This repo contains python app with custom metrics and prometheus/grafana stack to monitor the application!


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
