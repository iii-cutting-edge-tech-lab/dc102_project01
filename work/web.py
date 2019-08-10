# 引用設定
import boto3

# 服務名稱
bucketName = 'vcloudlab-bucket'
queueName = 'vcloudlab_sqs_queue'
tableName = 'vcloudlab_picture'
baseURL = "https://vcloudlab-bucket.s3-ap-northeast-1.amazonaws.com/"


# 服務連線
sqs_resource = boto3.resource('sqs')
sqs_client = boto3.client('sqs')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# 調用 SQS
vlabQueues = sqs_client.list_queues( QueueNamePrefix = queueName )
queue_url = vlabQueues['QueueUrls'][0]
print(queue_url)

# 用 flask 建立上傳環境
import os
import datetime
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'pic/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'chickenleg'

# function
def send_message(filename):

    # 調用 SQS
    vlabQueues = sqs_client.list_queues( QueueNamePrefix = queueName )
    queue_url = vlabQueues['QueueUrls'][0]
    # print(queue_url)

    # 將 filename 透過 SQS 傳輸
    enqueue_response = sqs_client.send_message(
        QueueUrl = queue_url,
        MessageBody = filename
    )
    # print('Message ID : ',enqueue_response['MessageId'])
    return True

# 解析檔案名稱
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 建立轉址位址
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/test')
def test():
    return "我是測試的"

# 建立上傳網址
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        #if 'file' not in request.files:
        #    flash('No file part')
        #    return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 儲存在 jupyter 本地端
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # 上傳到 S3
            s3_resource.meta.client.upload_file(
                'pic/'+str(filename), 
                bucketName, 
                str(filename)
            )
            
            # 將 filename 透過 SQS 傳輸
            send_message(filename)
            
            #enqueue_response = sqs_client.send_message(
            #    QueueUrl = queue_url, 
            #    MessageBody = filename
            #)
            #print('Message ID : ',enqueue_response['MessageId'])
            
            return "上傳成功"
            #return redirect(request.url)
            #return redirect(
            #    url_for('uploaded_file',
            #            filename = filename)
            #)
           
    return '''
    <!doctype html>
    <title>Web Application Demo</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


# 啟動 flask
app.run(host='0.0.0.0')
