from potassium import Potassium, Request, Response

from transformers import pipeline
from utils import download_payload_from_gcs
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

    prompt = download_payload_from_gcs(payload_file)
    print(prompt)
    outputs = model(prompt)

    return Response(
        json = {"outputs": outputs[0]}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()