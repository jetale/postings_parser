FROM ubuntu:jammy

RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y wget gnupg ca-certificates
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget curl unzip xvfb libxi6 libgconf-2-4\
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN wget --no-verbose -O chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.72/linux64/chromedriver-linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip \
    && rm -r chromedriver-linux64

COPY . /app/

RUN pip install .

ENV PYTHONPATH "${PYTHONPATH}:/app/"
RUN apt-get remove -y wget curl unzip gnupg ca-certificates

CMD ["bash", "postings_parser/backend/start_scrapers.sh"]
