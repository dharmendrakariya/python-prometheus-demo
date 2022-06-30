FROM python:3.10-slim-buster
WORKDIR /app
COPY . .
RUN pip3.10 install -r requirements.txt
CMD ["python3", "api.py", "flask", "run", "-p", "8080"]
