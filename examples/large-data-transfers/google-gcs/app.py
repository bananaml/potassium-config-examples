from potassium import Potassium, Request, Response
from transformers import pipeline
import utils
import torch
import os
import boto3
import string
import random
import os
from google.cloud import storage

app = Potassium("my_app")

def download_payload_from_gcs(file_name='example.txt'):
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
    prompt = download_payload_from_gcs(payload_file) # or download_payload_from_s3(...)
    outputs = model(prompt)

    # If the output is large as well, we'll upload the result to third-party storage, the client can then download it
    path = upload_payload_to_gcs(outputs[0]['sequence']) # or some other 3rd party storage e.g., upload_payload_to_s3(...)
    print(f"Output uploaded to: {path}")

    return Response(
        json = {"output_path": path}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()