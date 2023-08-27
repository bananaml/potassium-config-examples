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

    prompt = utils.download_payload_from_s3(payload_file)
    outputs = model(prompt)
    utils.upload_content_to_s3(outputs[0]['sequence'])


    return Response(
        json = {"outputs": outputs[0]}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()