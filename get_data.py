import boto3
import requests
from datetime import date, datetime, timedelta
import json
import pandas as pd
import os

access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

print(access_key_id is not None)
print(secret_access_key is not None)

s3 = boto3.client("s3", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

one_week_ago = date.today() - timedelta(days = 7)
one_week_ago = one_week_ago.strftime("%Y-%m-%d")

url  = "https://api.luchtmeetnet.nl/open_api"
measurements = url + "/measurements?start=" + one_week_ago + "T09%3A00%3A00Z&end=" + date.today().strftime("%Y-%m-%d") + "T09%3A00%3A00Z"

try: 
    data = requests.get(measurements)
    print(data.status_code)

    json_data = data.json()
    dict = json.loads(data.text)
    df = pd.json_normalize(dict)

    file_name = "air_quality-" + date.today().strftime("%Y-%m-%d") + ".csv"
    key = "air-quality/" + file_name

    df.to_csv(file_name, index=False)

    s3.upload_file(
        Filename=file_name,
        Bucket="pipeline-project-bucket-419",
        Key=key
    )
    os.remove(file_name)

except requests.exceptions.Timeout:
    print(f"Unable to fetch data.")

print(data)
