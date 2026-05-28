from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# GET DATA
# =========================

def get_table(table_name):
    response = supabase.table(table_name).select("*").execute()

    if response.data:
        return pd.DataFrame(response.data)

    return pd.DataFrame()


# =========================
# INSERT DATA
# =========================

def insert_data(table_name, data):
    return supabase.table(table_name).insert(data).execute()


# =========================
# UPDATE DATA
# =========================

def update_data(table_name, data, column, value):
    return (
        supabase.table(table_name)
        .update(data)
        .eq(column, value)
        .execute()
    )


# =========================
# DELETE DATA
# =========================

def delete_data(table_name, column, value):
    return (
        supabase.table(table_name)
        .delete()
        .eq(column, value)
        .execute()
    )