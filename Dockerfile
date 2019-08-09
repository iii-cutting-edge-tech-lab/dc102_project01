
# 用 flask 建立上傳環境
import os
import datetime
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/home/jovyan/work/pic/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'chickenleg'

# 解析檔案名稱


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pre_show():
    
    from flask_table import Table, Col, LinkCol

    
    class ItemTable(Table):
        ID = Col('ID')
        Filename = Col('Filename')
        Url = LinkCol('FileURL', 'link_for_click', url_kwargs=dict(id='ID'),attr='Url', anchor_attrs={'class': 'Url'})
        Datetime = Col('Datetime')
        Link = Col('Url', show=False)
        #ID2 = ID
        
#         def __init__(self):
#             return self.Url
        
#         def __repr__(self):
#             return str(self.Url)
    
    ID_MAX = vlabTable.item_count

    class Items(object):
        def __init__(self, ID, Filename, Url, Datetime):
            self.ID = ID
            self.Filename = Filename
            self.Url = Url
            self.Datetime = Datetime
            
#         @classmethod
#         def get_elements(cls):
#             return [
#             Item('cls', 'Filename', 'Url', 'Datetime')]
#         @classmethod
#         def get_element_by_id(cls, id):
#             return [i for i in cls.get_elements() if i.id == id][0]

            
    if ID_MAX == 0 :
        items = [Items(' ',' ',' ',' ')]
        table = ItemTable(items,border="1")

    else :
        for item_id in range(1,ID_MAX+1):
            response = vlabTable.get_item(
                Key={
                    'id': str(item_id),
                }
            )

            item = response['Item']

            if item_id == 1 :
                items = [Items(item['id'], item['filename'],
                        item['fileurl'], item['datetime'])]
            else : 
                items += [Items(item['id'], item['filename'], 
                        item['fileurl'], item['datetime'])]
#                 print(list(items))
#                 print('HI')
            

        table = ItemTable(items,border="1")
        #print(table.__html__())
#         a=table.ID
#         print(a[1][1])

    

    
    return table,items



def show_table(table):
    from flask import render_template

    return render_template('table.html',table=table)

a,items_ALL=pre_show()
#print(items_ALL)
# 建立轉址位址
from flask import send_from_directory

@app.route('/show/<int:id>')
def link_for_click(id):
    import webbrowser
    id_true = id - 1
    URL = items_all[id_true].Url
    #print(URL)
    a_website = "https://www.google.com"
    #webbrowser.open_new_tab(a_website)
    #webbrowser.get('chrome %s').open_new_tab('http://www.google.com')
    return redirect(URL)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
@app.route('/show', methods=['GET', 'POST'])
def show():
#    if request.method == 'POST':       
    if request.form.get('back') == "back":
        return redirect(url_for('upload_file'))
    global items_all
    table,items_all = pre_show()
    
    #print(items_all[1].Url)
    return show_table(table)

# 建立上傳網址
@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        
        if request.form.get('Upload') == "Upload":
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                                # 儲存在 jupyter 本地端
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                        # 上傳到 S3
                s3_resource.meta.client.upload_file(
                    '/home/jovyan/work/pic/'+str(filename), 
                    bucketName, 
                    str(filename)
                )

                enqueue_response = sqs_client.send_message(
                    QueueUrl = queue_url, 
                    MessageBody = filename
                )
                print('Message ID : ',enqueue_response['MessageId'])
                
                                            # 透過 SQS  將 filename 抓取
                while True:
                    messages = sqs_client.receive_message(
                      QueueUrl = queue_url,
                      MaxNumberOfMessages = 10
                    ) 
                    if 'Messages' in messages: 
                        for message in messages['Messages']: # 'Messages' is a list
                            # process the messages
                            print(message['Body'])

                            # 先判斷目前的 id
                            getId = vlabTable.item_count
                            setId = getId+1

                            # 將取得的 filename 存入 dynamodb
                            time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                            vlabTable.put_item(
                               Item = {
                                   'id': str(setId),
                                   'datetime': str(time),
                                   'fileurl': str(baseUrl)+str(filename),
                                   'filename': str(filename),
                               }
                            )

                            # 將在SQS佇列的Message刪除
                            sqs_client.delete_message(
                              QueueUrl = queue_url,
                              ReceiptHandle=message['ReceiptHandle']
                            )
                    else:
                        print('Queue is now empty')
                        break


                return '''
                <!doctype html>
                <title>Upload Success</title>
                <style>
                div {
                  background-image: linear-gradient(white, green);
                }
                body {
                  background-image: url("https://i.imgur.com/W7d0Df4.png");
                  background-repeat: no-repeat;
                  background-position: top right;
                  background-size: 660px 820px;
                }
                h1,h2 {
                  font-family: verdana;
                  text-shadow: 2px 2px 5px green;
                }
                </style>
                <h1>Upload Success</h1>
                <br>
                <br>
                <form method=post>
                  <input type=submit value=back name=back>
                </form>
                '''

        elif request.form.get('back', None) == "back":
            if request.form.get('back') == "back":
                return redirect(url_for('upload_file'))
        
        elif request.form.get('show', None) == "show":
            return redirect(url_for('show'))


        else :
            return "上傳失敗"
            


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <style>
    div {
      background-image: linear-gradient(white, green);
    }
    
    h1,h2 {
      font-family: verdana;
      text-shadow: 2px 2px 5px green;
    }

    body {
      background-image: url("https://i.imgur.com/W7d0Df4.png");
      background-repeat: no-repeat;
      background-position: top right;
      background-size: 660px 820px;
    }
    </style>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload name=Upload>
    </form>
    <br>
    <br>
    <h2>Show DynamoDB Table</h2>
    <form method=post>
      <input type=submit value=show name=show>
    </form>
    '''
app.run(host='0.0.0.0',prot=5000)
