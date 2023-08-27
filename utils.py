"""
    This file contains utility functions for common pre/post-processing required to use Banana
    You can copy any of these functions directly & standalone. Assuming you've setup your environment correctly, they should work
    See https://docs.banana.dev/banana-docs/core-concepts/potassium-your-models-server/configuring-potassium for more details on how to use these functions
"""
def download_payload_from_gcs(file_name='example.txt'):
    import os
    from google.cloud import storage

    """
        If you need to create application credentials for accessing google cloud storage, read https://developers.google.com/workspace/guides/create-credentials
        tl;dr
        Go to the Google Cloud Console (https://console.cloud.google.com/).
        Create a new project or use an existing one.
        In the left navigation pane, go to "IAM & Admin" > "Service accounts".
        Create a new service account or use an existing one.
        Generate a new key for the service account in JSON format.
        Save the downloaded JSON key file to a secure location on your system
    """

    # Assuming your have gcloud_credentials.json in the same directory as this utils.py file, this line sets the GOOGLE_APPLICATION_CREDENTIALS line to point to it
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.getcwd(), "gcloud_credentials.json"
    )

    # You can set your Google Cloud Storage bucket and folder from environment variables (here we're hard coding some example bucket/folder for simplicity, your naming will vary)
    bucket_name = "example-remote-bucket"
    folder_name = "inputs"

    # Initialize the Google Cloud Storage client
    client = storage.Client()

    # Get a reference to the bucket
    bucket = client.get_bucket(bucket_name)

    # Construct the full path to the image file in GCS
    remote_path = os.path.join(folder_name, file_name)

    # Get a blob reference to the image file
    blob = bucket.blob(remote_path)

    # Download the text and save in payload
    payload = blob.download_as_text()

    # alternatively you could download any file type to machine or variable, and then convert it into the .wav etc you need
    # local_path = os.path.join(os.getcwd(), file_name)
    # blob.download_to_filename(local_path)

    return payload

def download_payload_from_s3(file_name='example.txt'):
    # This assumes you've setup an AWS S3 bucket and have the credentials stored in the same directory as this code in a .env file
    # required contents of .env file:
    # AWS_ACCESS_KEY_ID=...
    # AWS_SECRET_ACCESS_KEY=...
    # AWS_REGION=...

    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    import os
    import boto3

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

def upload_payload_to_gcs(content):
    """
        If you need to create application credentials for accessing google cloud storage, read https://developers.google.com/workspace/guides/create-credentials
        tl;dr
        Go to the Google Cloud Console (https://console.cloud.google.com/).
        Create a new project or use an existing one.
        In the left navigation pane, go to "IAM & Admin" > "Service accounts".
        Create a new service account or use an existing one.
        Generate a new key for the service account in JSON format.
        Save the downloaded JSON key file to a secure location on your system
    """

    import os
    from google.cloud import storage
    import string
    import random

    bucket_name = "example-remote-bucket"
    folder_name = "outputs"

    # Initialize the Google Cloud Storage client
    client = storage.Client()

    # Get a reference to the bucket
    bucket = client.get_bucket(bucket_name)

    # Construct the destination path within the bucket
    rand_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    destination_key = os.path.join(folder_name, "output_" + rand_suffix + ".txt")

    # Upload the content to the specified GCS location
    blob = bucket.blob(destination_key)
    blob.upload_from_string(content)

    output_path = bucket_name + "/ " + destination_key
    return output_path

def upload_payload_to_s3(payload):
    # This assumes you've setup an AWS S3 bucket and have the credentials stored in the same directory as this code in a .env file
    # required contents of .env file:
    # AWS_ACCESS_KEY_ID=...
    # AWS_SECRET_ACCESS_KEY=...
    # AWS_REGION=...

    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    
    import os
    import boto3
    import string
    import random

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