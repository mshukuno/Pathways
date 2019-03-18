FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y software-properties-common build-essential python3-pip  nano && \
    apt-get clean

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8050
CMD ["python3", "run.py"]

