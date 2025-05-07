# supabase_auth.py
import os
import bcrypt
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(email, password):
    # Check if user already exists
    response = supabase.table("users").select("*").eq("email", email).execute()
    if response.data:
        return False, "User already exists"

    hashed_pw = hash_password(password)
    supabase.table("users").insert({"email": email, "password": hashed_pw}).execute()
    return True, "User registered successfully"

def authenticate_user(email, password):
    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        return False, "User not found"

    user = response.data[0]
    if verify_password(password, user["password"]):
        return True, user
    else:
        return False, "Incorrect password"
