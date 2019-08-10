# load default image
FROM python:3.6

# add project
COPY ./work /work/
COPY ./.aws /.aws/
WORKDIR /work

# install flask
RUN pip install -r requirements.txt
RUN pip install PyMySQL
RUN pip install boto3
RUN pip install awscli
RUN pip install flask
RUN pip install pytz
# run flask
#ENTRYPOINT ["python"]
#CMD ["test_flask.py"]

#RUN /bin/bash -c 'python test_flask.py'

# run flask
ENV AWS_ACCESS_KEY_ID=AKIAS7A2A5TDS377W32G
ENV AWS_SECRET_ACCESS_KEY=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
ENV  AWS_DEFAULT_REGION=ap-northeast-1
ENTRYPOINT ["python"]
CMD ["web.py"]

