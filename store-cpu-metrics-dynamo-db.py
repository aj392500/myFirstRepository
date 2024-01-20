import boto3
import json
import time
# Create a SSM client
ssm_client = boto3.client('ssm',region_name='ap-south-1')
parameter_name1 = 'dynamodbtablename'
parameter_name2 = 'sqsurl'
dynamodbtablename_response = ssm_client.get_parameter(Name=parameter_name1,WithDecryption=False)  # Decrypt if parameter is encrypted
sqsurl_response = ssm_client.get_parameter(Name=parameter_name2,WithDecryption=False)  # Decrypt if parameter is encrypted
# Replace with your DynamoDB queue URL
queue_name = sqsurl_response['Parameter']['Value']
table_name = dynamodbtablename_response['Parameter']['Value']
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
