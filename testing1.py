from keys import SUPABASE_URL, SUPABASE_ANON_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print(supabase.table("movies").select("*").execute().data)
print(supabase.table("cinematheques").select("*").execute().data)
