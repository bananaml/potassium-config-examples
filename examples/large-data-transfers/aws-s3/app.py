from potassium import Potassium, Request, Response
from transformers import pipeline
import utils
import torch
import os
import boto3
import string
import random
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
 

app = Potassium("my_app")

def upload_payload_to_s3(payload):
    # This assumes you've setup an AWS S3 bucket and have the credentials stored in the same directory as this code in a .env file
    # required contents of .env file:
    # AWS_ACCESS_KEY_ID=...
    # AWS_SECRET_ACCESS_KEY=...
    # AWS_REGION=...
    
    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = 'model-payloads'
    folder_name = 'outputs'  # Folder within the bucket

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Construct the destination key within the bucket
    rand_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    destination_key = os.path.join(folder_name, "output_" + rand_suffix + ".txt")

    # Upload the payload to the specified S3 location
    s3.put_object(Body=payload, Bucket=bucket_name, Key=destination_key)

    output_path = bucket_name + "/" + destination_key
    return output_path
def download_payload_from_s3(file_name='example.txt'):
    # This assumes you've setup an AWS S3 bucket and have the credentials stored in the same directory as this code in a .env file
    # required contents of .env file:
    # AWS_ACCESS_KEY_ID=...
    # AWS_SECRET_ACCESS_KEY=...
    # AWS_REGION=...

    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    bucket_name = 'model-payloads'
    folder_name = 'inputs'  # Folder within the bucket

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # print all folders in model-payloads bucket
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    # Construct the source key within the bucket
    source_key = os.path.join(folder_name, file_name)

    # Download the content from the specified S3 location
    response = s3.get_object(Bucket=bucket_name, Key=source_key)
    payload = response['Body'].read().decode('utf-8')

    return payload

# @app.init runs at startup, and loads models into the app's context
@app.init
def init():
    device = 0 if torch.cuda.is_available() else -1
    model = pipeline('fill-mask', model='bert-base-uncased', device=device)
   
    context = {
        "model": model
    }

    return context

# @app.handler runs for every call
@app.handler("/")
def handler(context: dict, request: Request) -> Response:
    payload_file = request.json.get("payload_file")
    model = context.get("model")

    # It's assumed the client uploaded the large payload to some third party storage, and we can fetch it by file name
    prompt = download_payload_from_s3(payload_file) # or download_payload_from_s3(...)
    outputs = model(prompt)

    # If the output is large as well, we'll upload the result to third-party storage, the client can then download it
    path = upload_payload_to_s3(outputs[0]['sequence']) # or some other 3rd party storage e.g., upload_payload_to_s3(...)
    print(f"Output uploaded to: {path}")

    return Response(
        json = {"output_path": path}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()