import subprocess
import sys

result = subprocess.run(
    [r'E:\code\PrometheusBot\backend\venv\Scripts\python.exe', '-m', 'pytest', 'tests/', '-v'],
    cwd=r'E:\code\PrometheusBot\backend',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)
