FROM python:3

# Server
WORKDIR /usr/src/pelican-server
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "src/pelicanserver.py" ]

# Frontend
#FROM node
#WORKDIR /usr/src/pelican-server
