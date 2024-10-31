@echo off
cd "C:\Users\Engineer99\Documents\Davis Class\OCR"
call .\venv\Scripts\activate
python .\local_llm_test.py -d .\data\data_01\
python .\local_llm_test.py -d .\data\combined_data\