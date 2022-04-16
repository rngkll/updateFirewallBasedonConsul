FROM python:3.9-slim-bullseye

RUN apt update && apt -y install firewalld

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "configureFirewall.py"]
