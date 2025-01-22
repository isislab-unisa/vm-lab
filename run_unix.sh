#!/bin/bash
# Activate the virtual environment and run streamlit

if [ -d ".venv" ]; then
  source .venv/bin/activate
  streamlit run app.py
else
  echo "The .venv does not exist."
  exit 1
fi
