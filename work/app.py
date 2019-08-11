import boto3

# varible
tableName = 'vcloudlab_picture'
bucketName = 'vcloudlab_bucket'
queueName = 'vcloudlab_sqs_queue'
baseURL = "https://vcloudlab-bucket.s3-ap-northeast-1.amazonaws.com/"

# 服務連線
sqs_client = boto3.client(
    'sqs')
sqs_resource = boto3.resource(
    'sqs')

dynamoDB_client = boto3.client(
    'dynamodb')
dynamoDB_resource = boto3.resource(
    'dynamodb')

# 調用 SQS
vlabQueues = sqs_client.list_queues( QueueNamePrefix = queueName )
queue_url = vlabQueues['QueueUrls'][0]
print(queue_url)

# 調用 dynamoDB Table
vlabTable = dynamoDB_resource.Table(tableName)
print(vlabTable)

import datetime
# 透過 SQS  將 filename 抓取
while True:
    messages = sqs_client.receive_message(
        QueueUrl = queue_url,
        MaxNumberOfMessages = 1,
        WaitTimeSeconds = 20
    )

    if 'Messages' in messages:
        for message in messages['Messages']:
#             print(message['Body'])
            filename = message['Body']
            # 先判斷目前的 id
            getId = vlabTable.item_count
            setId = getId+1
            print(filename + ":"+str(setId))
            # 將取得的 filename 存入 dynamodb
            time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            vlabTable.put_item(
                Item = {
                    'id': str(setId),
                    'datetime': str(time),
                    'fileurl': str(baseURL)+str(filename),
                    'filename': str(filename),
                }
            )

            sqs_client.delete_message(
                QueueUrl = queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
    else:
        print('Queue is now empty')
