FROM python:3.8
WORKDIR /project
ADD . /project

# environment needed for proxy server on ahc servers
#ENV HTTP_PROXY="http://ctsigate0.ahc.umn.edu:3128" 
#ENV HTTPS_PROXY="http://ctsigate0.ahc.umn.edu:3128"

RUN pip install -r requirements_docker.txt

CMD ["python","app1.py"]