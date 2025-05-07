import os
import bcrypt
import uuid
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key is not set.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(email, password):
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            return False, "User already exists"

        hashed_pw = hash_password(password)
        user_id = str(uuid.uuid4())  # fallback if Supabase doesn't generate it
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "password": hashed_pw
        }).execute()
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(email, password):
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response.data:
            return False, None, "User not found"

        user = response.data[0]
        if verify_password(password, user["password"]):
            if "id" not in user:
                user["id"] = user.get("user_id", str(uuid.uuid4()))  # ensure ID is available
            return True, user, "Login successful"
        else:
            return False, None, "Incorrect password"
    except Exception as e:
        return False, None, f"Login error: {str(e)}"