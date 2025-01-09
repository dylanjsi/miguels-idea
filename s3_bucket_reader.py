import boto3
import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime
from urllib.parse import urlparse
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def read_json_from_s3(bucket_name, file_key):
    try:
        # Get the object from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        # Read and parse JSON content
        file_content = response['Body'].read().decode('utf-8')
        return json.loads(file_content)
    except Exception as e:
        print(f"Error reading {file_key}: {e}")
        return None

def extract_photo_urls(json_data):
    photo_urls = []
    
    if isinstance(json_data, list):
        for item in json_data:
            if isinstance(item, dict) and 'photos' in item:
                photos = item['photos']
                if isinstance(photos, list):
                    photo_urls.extend([url for url in photos if isinstance(url, str)])
    elif isinstance(json_data, dict):
        if 'photos' in json_data:
            photos = json_data['photos']
            if isinstance(photos, list):
                photo_urls.extend([url for url in photos if isinstance(url, str)])
    
    return photo_urls

def download_and_resize_photo(url, output_dir, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Open image from response content
        img = Image.open(io.BytesIO(response.content))
        
        # Resize image to 128x128 using LANCZOS resampling
        img = img.resize((128, 128), Image.Resampling.LANCZOS)
        
        # Save resized image
        file_path = os.path.join(output_dir, filename)
        img.save(file_path, "JPEG")
        return True
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return False

def process_bucket_json_files(bucket_name):
    try:
        # Create output directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('downloaded_photos', timestamp)
        ensure_directory_exists(output_dir)
        
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print("Bucket is empty")
            return

        # Process JSON files
        print(f"Processing JSON files in bucket '{bucket_name}':")
        for obj in response['Contents']:
            if obj['Key'].endswith('.json'):
                print(f"\nProcessing JSON file: {obj['Key']}")
                json_data = read_json_from_s3(bucket_name, obj['Key'])
                
                if json_data:
                    photo_urls = extract_photo_urls(json_data)
                    if photo_urls:
                        # Create a subdirectory for this JSON file's photos
                        base_name = os.path.splitext(os.path.basename(obj['Key']))[0]
                        photo_dir = os.path.join(output_dir, base_name)
                        ensure_directory_exists(photo_dir)
                        
                        # Download and resize each photo
                        success_count = 0
                        for i, url in enumerate(photo_urls):
                            # Create a safe filename
                            filename = f"{base_name}_{i}.jpg"
                            
                            if download_and_resize_photo(url, photo_dir, filename):
                                success_count += 1
                                print(f"Downloaded and resized {filename}")
                        
                        print(f"Successfully processed {success_count}/{len(photo_urls)} photos")
                    else:
                        print("No photo URLs found in this file")
                print("-" * 40)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    bucket_name = 'closodex-apify-pull'  # Replace with your bucket name
    process_bucket_json_files(bucket_name) 