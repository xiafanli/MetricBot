@echo off
cd E:\code\PrometheusBot\backend
E:\code\PrometheusBot\backend\venv\Scripts\python.exe -m pytest tests/ -v > test_output.txt 2>&1
type test_output.txt
