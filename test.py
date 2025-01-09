import boto3
import json
import os

# Debugging
import logging
boto3.set_stream_logger(name='botocore')

# Set environment variables
os.environ["AWS_ACCESS_KEY_ID"] = "AKIAUPMYNFIB35TQDOQQ"
os.environ["AWS_SECRET_ACCESS_KEY"] = "mY7jy0TscwBC3xyoR1pXUnK5aLWp"
# s3_client = boto3.client('s3', region_name='us-east-2')
def read_json_from_s3(bucket_name, file_name):
    try:
        # Explicitly specify the region
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-2'  # Replace with your bucket's actual region
        )

        # Fetch the file content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)

        # Read the file content and parse JSON
        file_content = response['Body'].read().decode('utf-8')
        json_data = json.loads(file_content)

        return json_data
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage
bucket_name = 'closodex-apify-pull'
file_name = 'all-burrows-for-rent-1735971067200.json'  # Replace with the actual file name

json_data = read_json_from_s3(bucket_name, file_name)
if json_data:
    print(json.dumps(json_data, indent=2))
else:
    print("Failed to read JSON from S3.")