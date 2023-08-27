from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
def download_payload_from_gcs(file_name='example.txt'):
    import os
    from google.cloud import storage

    """
        If you need to create application credentials for accessing google cloud strorage, read https://developers.google.com/workspace/guides/create-credentials
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

    # Download the text and save in text_content
    text_content = blob.download_as_text()

    # alternatively you could download any file type to machine or variable, and then convert it into the .wav etc you need
    # local_path = os.path.join(os.getcwd(), file_name)
    # blob.download_to_filename(local_path)

    return text_content

def download_payload_from_s3(file_name='example.txt'):
    import os
    import boto3

    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    print(aws_access_key_id, aws_secret_access_key)
    bucket_name = 'model-payloads'
    folder_name = 'inputs'  # Folder within the bucket

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


    # print all folders in model-payloads bucket
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    print(response)
    # Construct the source key within the bucket
    source_key = os.path.join(folder_name, file_name)
    print(source_key)

    # Download the content from the specified S3 location
    response = s3.get_object(Bucket=bucket_name, Key=source_key)
    content = response['Body'].read().decode('utf-8')

    return content

def upload_content_to_gcs(content):
    import os
    from google.cloud import storage

    bucket_name = "example-remote-bucket"
    folder_name = "outputs"

    # Initialize the Google Cloud Storage client
    client = storage.Client()

    # Get a reference to the bucket
    bucket = client.get_bucket(bucket_name)

    # Construct the destination path within the bucket
    destination_blob_name = os.path.join(folder_name, 'output.txt')  # Change 'output.txt' as needed

    # Upload the content to the specified GCS location
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(content)

    print(f"Content uploaded to: gs://{bucket_name}/{destination_blob_name}")

def upload_content_to_s3(content):
    import os
    import boto3

    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = 'model-payloads'
    folder_name = '/outputs'  # Folder within the bucket

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Construct the destination key within the bucket
    destination_key = os.path.join(folder_name, 'output.txt')  # Change 'output.txt' as needed

    # Upload the content to the specified S3 location
    s3.put_object(Body=content, Bucket=bucket_name, Key=destination_key)

    print(f"Content uploaded to: s3://{bucket_name}/{destination_key}")

