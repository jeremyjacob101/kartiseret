def find_3d_movies():
    from supabase import create_client
    import os, re

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    def contains_3d(row, excluded_cols):
        for col, val in row.items():
            if col not in excluded_cols and isinstance(val, str):
                if re.search(r"\b3d\b", val, re.IGNORECASE):
                    return True
        return False

    def get_rows_with_3d(table_name, excluded_cols):
        response = supabase.table(table_name).select("*").execute()
        rows = response.data or []
        return [r for r in rows if contains_3d(r, excluded_cols)]

    excluded = {
        "testingMovies": ["showtime_id"],
        "testingSoons": ["coming_soon_id"],
        "testingTheques": ["theque_showtime_id"],
    }

    movies_3d = get_rows_with_3d("testingMovies", excluded["testingMovies"])
    soons_3d = get_rows_with_3d("testingSoons", excluded["testingSoons"])
    theques_3d = get_rows_with_3d("testingTheques", excluded["testingTheques"])

    print("🎬 Movies with '3D':", movies_3d)
    print("📅 Coming Soons with '3D':", soons_3d)
    print("🏛️ Theques with '3D':", theques_3d)
