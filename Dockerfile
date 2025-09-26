FROM python:3.9
WORKDIR /app

# environment needed for proxy server on ahc servers
ENV HTTP_PROXY="http://ctsigate.ahc.umn.edu:3128" 
ENV HTTPS_PROXY="http://ctsigate.ahc.umn.edu:3128"

# upgrade pip
RUN pip install --upgrade pip

COPY requirements.txt .


# install the necessary packages
RUN pip install -r requirements.txt


COPY .env .

COPY . .

# environment values are store in .env

EXPOSE 5000

CMD ["python","app_usercode.py"]

# CMD ["python","fitbit_flask.py"]
