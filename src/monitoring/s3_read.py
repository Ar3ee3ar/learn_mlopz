import dvc.api
from io import StringIO
import boto3
import os

from shared.config_loader import load_environment

load_environment()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')

def get_s3(object_file):
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket_name = BUCKET_NAME
    object_key = f'data/{object_file}'
    print(object_key)
    objects_list = s3_client.list_objects_v2(Bucket=bucket_name).get("Contents")
    print(objects_list)
    exit(0)
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    object_content = response['Body'].read().decode('utf-8')
    return object_content

def get_dvc(object_file):
    # Replace with your actual path, repository URL, and revision
    file_path = f"data/{object_file}"
    repo_url = os.getenv("REPO_URI") # Or your Git repo
    revision = "main" # Or a specific commit hash/tag

    # try:
    with dvc.api.open(
        path=file_path,
        repo=repo_url,
        rev=revision
    ) as f:
        # f is a file-like object, you can process its content
        # For example, reading a CSV into a pandas DataFrame:
        contents = f.read()
        data = pd.read_csv(StringIO(contents))
        print("Successfully read data:")
        print(data.head())
    # except Exception as e:
    #     print(f"Error accessing DVC file: {e}")

if __name__ == "__main__":
    #get_s3('train.csv')
    get_dvc('train.csv')
