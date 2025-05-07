# supabase_auth.py
import os
import bcrypt
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate env variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key is not set in environment variables.")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Register new user
def register_user(email, password):
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            return False, "User already exists"

        hashed_pw = hash_password(password)
        supabase.table("users").insert({"email": email, "password": hashed_pw}).execute()
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

# Authenticate and log in user
def login_user(email, password):
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response.data:
            return False, None, "User not found"

        user = response.data[0]
        if verify_password(password, user["password"]):
            return True, user["id"], "Login successful"
        else:
            return False, None, "Incorrect password"
    except Exception as e:
        return False, None, f"Login error: {str(e)}"

