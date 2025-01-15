@echo off
REM Activate the virtual environment and run streamlit Streamlit

if exist ".venv\" (
    call .venv\Scripts\activate
    streamlit run app.py
) else (
    echo The .venv does not exist.
    exit /b 1
)
