FROM centos/python-36-centos7

RUN yum update -y

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -R requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD ["index.py"]