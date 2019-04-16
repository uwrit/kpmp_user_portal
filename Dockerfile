FROM centos/python-36-centos7
USER root
RUN yum update -y

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5001
ENTRYPOINT [ "python", "index.py" ]
