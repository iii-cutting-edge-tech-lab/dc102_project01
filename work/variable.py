import boto3

# varible
tableName = 'vcloudlab_picture'
bucketName = 'vcloudlab_bucket'
queueName = 'vcloudlab_sqs_queue'

#s3_endpoint_url = 'http://s3.vcloudlab.pro:4569'
#sqs_endpoint_url = 'http://sqs.vcloudlab.pro:9324'
#dynamoDB_endpoint_url = 'http://dynamodb.vcloudlab.pro:8000'

baseURL = "https://vcloudlab-bucket.s3-ap-northeast-1.amazonaws.com/"

s3_client = boto3.client(
    's3')
s3_resource = boto3.resource(
    's3')

sqs_client = boto3.client(
    'sqs')
sqs_resource = boto3.resource(
    'sqs')

dynamoDB_client = boto3.client(
    'dynamodb')
dynamoDB_resource = boto3.resource(
    'dynamodb')

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
