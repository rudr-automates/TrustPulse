import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)

email = input("Test user email: ").strip()
password = input("Test user password: ").strip()

response = supabase.auth.sign_in_with_password(
    {
        "email": email,
        "password": password,
    }
)

if not response.session:
    raise RuntimeError("Authentication failed.")

print("\nAccess token:\n")
print(response.session.access_token)