import os
import boto3
import json
import uuid
import logging
from chalice import Chalice

app = Chalice(app_name="image_converter")

# Setup logging for debugging purposes
app.log.setLevel(logging.DEBUG)

DEST_BUCKET = ""
if "DEST_BUCKET" in os.environ:
    DEST_BUCKET = str(os.environ["DEST_BUCKET"])
    app.log.info(f"Setting the destination bucket: {DEST_BUCKET}")
else:
    app.log.debug(f"Couldn't process the DEST_BUCKET environment variable. ")

ORIGIN_BUCKET = ""
if "ORIGIN_BUCKET" in os.environ:
    ORIGIN_BUCKET = str(os.environ["ORIGIN_BUCKET"])
    app.log.info(f"Setting the origin bucket: {ORIGIN_BUCKET}. ")
else:
    app.log.debug(f"Couldn't process the ORIGIN_BUCKET environment variable. ")

@app.route('/')
def index():
    return {'hello': 'world'}

@app.on_s3_event(bucket=os.environ["ORIGIN_BUCKET"],
                 events=["s3:ObjectCreated:*"])
def image_converter(event):
    image_path = f"/tmp/image_{event.key}"
    session = boto3.session.Session(
        aws_access_key_id=os.environ["AWS_KEY"],
        aws_secret_access_key=os.environ["AWS_SECRET"]
    )
    s3 = session.client("s3")
    s3.download_file(event.bucket, event.key, image_path)

    image = Image.open(image_path)

    for image_type in ("png", "bmp", "gif"):
        result_path = f"/tmp/image_{uuid.uuid4().hex}.{image_type}"
        image.save(result_path)
        s3.upload_file(result_path, os.environ['DEST_BUCKET'], f"{uuid.uuid4().hex}.{image_type}")