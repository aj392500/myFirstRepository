import boto3
import json
import time
# Replace with your SQS queue name and DynamoDB table name
queue_name = 'https://sqs.ap-south-1.amazonaws.com/028093479336/DemoQueue'
table_name = 'cpumetrics'
# Create SQS and DynamoDB clients
sqs = boto3.client('sqs',region_name='ap-south-1')
dynamodb = boto3.client('dynamodb',region_name='ap-south-1')
while True:
  # Receive messages from the SQS queue
  response = sqs.receive_message(
      QueueUrl=queue_name,
      MaxNumberOfMessages=10,  # Adjust as needed
      VisibilityTimeout=60  # Set appropriate visibility timeout
  )
  messages = response.get('Messages', [])
  if messages:
      for message in messages:
          # Extract timestamp and CPU usage from the message body
          message_body = json.loads(message['Body'])
          timestamp = message_body['timestamp']
          cpuusage = message_body['cpu_usage']
          # Put the data into the DynamoDB table
          try:
              dynamodb.put_item(
                  TableName=table_name,
                  Item={
                      'timestamp': {'S': str(timestamp)},
                      'cpuusage': {'N': str(cpuusage)}
                  }
              )
              print(f"Successfully added timestamp {timestamp} and CPU usage {cpuusage} to DynamoDB.")
          except Exception as e:
              print(f"Error putting item in DynamoDB: {e}")
          # Delete the message from the SQS queue
          sqs.delete_message(
              QueueUrl=queue_name,
              ReceiptHandle=message['ReceiptHandle']
          )
  else:
      print('No messages in the queue.')
  # Wait for a few seconds before checking for new messages
  time.sleep(5)  # Adjust as needed