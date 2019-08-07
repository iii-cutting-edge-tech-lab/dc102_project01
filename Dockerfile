# 載入預設映像
FROM python:3.7

# 增加專案
ADD . /code
WORKDIR /code

# 安裝flask
RUN pip install flask


# run flask
#ENTRYPOINT ["python"]
#CMD ["test_flask.py"]

RUN /bin/bash -c 'python test_flask.py'


# 運行flask
ENTRYPOINT ["python"]
CMD python app.py
