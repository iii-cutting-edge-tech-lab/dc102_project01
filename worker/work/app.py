import boto3

# varible
tableName = 'vcloudlab_picture'
bucketName = 'vcloudlab_bucket'
queueName = 'vcloudlab_sqs_queue'
baseURL = "http://s3.vcloudlab.pro:4569/s3/vcloudlab_bucket/"
sqs_endpoint_url = 'http://sqs.vcloudlab.pro:9324'
dynamoDB_endpoint_url = 'http://dynamodb.vcloudlab.pro:8000'

# 服務連線
sqs_client = boto3.client(
    'sqs',
    endpoint_url = sqs_endpoint_url)
sqs_resource = boto3.resource(
    'sqs',
    endpoint_url = sqs_endpoint_url)

dynamoDB_client = boto3.client(
    'dynamodb',
    endpoint_url = dynamoDB_endpoint_url)
dynamoDB_resource = boto3.resource(
    'dynamodb',
    endpoint_url = dynamoDB_endpoint_url)

# 創建 DynamoDB Table
vlabTable = dynamoDB_resource.create_table(
    TableName = tableName,
    
    KeySchema = [
      {
          'AttributeName': 'id',
          'KeyType': 'HASH'
      },
        
    ],
    
    AttributeDefinitions = [
      {
          'AttributeName': 'id',
          'AttributeType': 'S'
      },
    ],
    
    ProvisionedThroughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
vlabTable.meta.client.get_waiter('table_exists').wait(TableName=tableName)

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
