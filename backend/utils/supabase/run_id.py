import os
from supabase import create_client


def allocate_run_id() -> int:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    rows = sb.table("utilAvgTime").select("latest_run_id").limit(1).execute().data
    new_id = int(rows[0].get("latest_run_id")) + 1
    sb.table("utilAvgTime").update({"latest_run_id": new_id}).neq("name", "__no_such_name__").execute()
    return new_id
