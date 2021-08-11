# Objective: Running selenium python scripts in alpine without grid

FROM python:3.9.6-alpine3.14

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apk add --no-cache bash &&\
    apk update &&\
    apk upgrade

RUN apk add chromium
RUN apk add chromium-chromedriver

# Get all the prereqs
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub
RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-2.30-r0.apk
RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-bin-2.30-r0.apk
RUN apk add glibc-2.30-r0.apk
RUN apk add glibc-bin-2.30-r0.apk

# And of course we need Firefox if we actually want to *use* GeckoDriver
RUN apk add firefox

# Then install GeckoDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
RUN tar -zxf geckodriver-v0.29.0-linux64.tar.gz -C /usr/bin
RUN geckodriver --version

EXPOSE 5000

ENV CHROME_BIN=/usr/bin/chromium-browser \
    CHROME_PATH=/usr/lib/chromium/

# CMD ["python", "cookiescanner.py"]

# run the image passing the .py file as parameter and that's it :)
