from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import os

# ==================================================
# CONFIG
# ==================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==================================================
# CONNECTION
# ==================================================

def get_supabase():
    return supabase


# ==================================================
# READ
# ==================================================

@st.cache_data(ttl=300)
def get_table(table_name):
    """
    Ambil seluruh data table dan return DataFrame.
    Cache 5 menit untuk mengurangi request Supabase.
    """

    response = (
        supabase
        .table(table_name)
        .select("*")
        .execute()
    )

    return pd.DataFrame(response.data or [])


def get_table_raw(table_name):
    """
    Ambil data tanpa cache.
    Dipakai untuk transaksi yang butuh data terbaru.
    """

    response = (
        supabase
        .table(table_name)
        .select("*")
        .execute()
    )

    return pd.DataFrame(response.data or [])


def get_by_column(table_name, column, value):
    """
    Ambil data berdasarkan 1 kondisi.
    """

    response = (
        supabase
        .table(table_name)
        .select("*")
        .eq(column, value)
        .execute()
    )

    return pd.DataFrame(response.data or [])


def get_single(table_name, column, value):
    """
    Ambil 1 row pertama.
    Return dict atau None.
    """

    response = (
        supabase
        .table(table_name)
        .select("*")
        .eq(column, value)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


# ==================================================
# CREATE
# ==================================================

def insert_data(table_name, data):
    """
    Insert 1 row atau list row.
    """

    return (
        supabase
        .table(table_name)
        .insert(data)
        .execute()
    )


# ==================================================
# UPDATE
# ==================================================

def update_data(table_name, data, column, value):
    """
    Update berdasarkan 1 kondisi.
    """

    return (
        supabase
        .table(table_name)
        .update(data)
        .eq(column, value)
        .execute()
    )


# ==================================================
# DELETE
# ==================================================

def delete_data(table_name, column, value):
    """
    Delete berdasarkan 1 kondisi.
    """

    return (
        supabase
        .table(table_name)
        .delete()
        .eq(column, value)
        .execute()
    )


# ==================================================
# EXISTS
# ==================================================

def exists(table_name, column, value):
    """
    Cek data ada atau tidak.
    """

    response = (
        supabase
        .table(table_name)
        .select(column)
        .eq(column, value)
        .limit(1)
        .execute()
    )

    return len(response.data) > 0


# ==================================================
# CACHE
# ==================================================

def clear_cache():
    st.cache_data.clear()