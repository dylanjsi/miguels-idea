# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)

# AWS credentials should also come from environment variables
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# If you need to debug/verify the tokens (be careful with this in production!)
print("AWS Access Key:", aws_access_key[:4] + '*' * (len(aws_access_key)-4) if aws_access_key else "Not set")
print("AWS Secret Key:", '*' * 8 if aws_secret_key else "Not set")


