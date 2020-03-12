**Initial push** **Not 100% sure**
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python-pip python-dev

ENV HOME /CSE-312-Web_Apps

WORKDIR /proj312

COPY . .

RUN pip install -r Dockerfile.txt

COPY . /__init__.py

EXPOSE 8000

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
