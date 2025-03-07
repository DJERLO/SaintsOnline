import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Get PayMongo secret key from env

username = os.getenv("PAYMONGO_SECRET_KEY")
password = ""
credentials = f"{username}:{password}"

# Encode in Base64
if credentials:
    credentials = base64.b64encode(credentials.encode()).decode()
    print(credentials)
else:
    raise ValueError("PAYMONGO_SECRET_KEY is not set in environment variables")