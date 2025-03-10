@echo off
cd /d \\servidor\aplicacoes\smart-edu-dashboard
python -m streamlit run main.py --server.address=0.0.0.0 --server.port=8501
