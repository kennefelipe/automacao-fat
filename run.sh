#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt -q 2>/dev/null
streamlit run app.py --server.headless true --server.port 8501
