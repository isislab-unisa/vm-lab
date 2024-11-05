import streamlit as st

from backend.database import get_db, User

with get_db() as db:
    users = db.query(User).all()

    user_data = []
    for user in users:
        user_data.append({
            "ID": user.id,
            "Username": user.username,
            "Email": user.email,
            "First Name": user.first_name,
            "Last Name": user.last_name,
            "Role": user.role
        })

    st.table(user_data)
