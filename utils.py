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
