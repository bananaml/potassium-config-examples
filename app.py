from potassium import Potassium, Request, Response

from transformers import pipeline
import utils
import torch

app = Potassium("my_app")

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
    prompt = utils.download_payload_from_s3(payload_file) # or download_payload_from_s3(...)
    outputs = model(prompt)

    # If the output is large as well, we'll upload the result to third-party storage, the client can then download it
    path = utils.upload_payload_to_s3(outputs[0]['sequence']) # or some other 3rd party storage e.g., upload_payload_to_s3(...)
    print(f"Output uploaded to: {path}")

    return Response(
        json = {"output_path": path}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()