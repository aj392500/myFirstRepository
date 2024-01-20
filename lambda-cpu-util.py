import psutil
import time
import json
import boto3
# Replace with your SQS queue URL
queue_url = 'https://sqs.ap-south-1.amazonaws.com/028093479336/DemoQueue'
# Create an SQS client
sqs_client = boto3.client('sqs', region_name='ap-south-1')
while True:
   cpu_usage = psutil.cpu_percent()
   timestamp = time.time()
   data = {"timestamp": timestamp, "cpu_usage": cpu_usage}
   message_body = json.dumps(data)
   try:
       response = sqs_client.send_message(
           QueueUrl=queue_url,
           MessageBody=message_body
       )
       print(f"Message sent to SQS: {message_body}")
   except Exception as e:
       print(f"Error sending message: {e}")
   time.sleep(60)  # Send data every 60 seconds