import subprocess
import sys

# 剩余需要安装的依赖
dependencies = [
    'uvicorn==0.15.0',
    'python-dotenv==0.20.0',
    'httpx==0.19.0',
    'pyyaml==5.4.1',
    'pytest==6.2.5',
    'black==21.12b0'
]

pip_path = '.\\venv\\Scripts\\pip.exe'
index_url = 'https://mirrors.aliyun.com/pypi/simple/'

for dep in dependencies:
    print(f'正在安装 {dep}...')
    try:
        subprocess.check_call([
            pip_path, 'install', dep,
            '-i', index_url
        ])
        print(f'{dep} 安装成功\n')
    except subprocess.CalledProcessError as e:
        print(f'{dep} 安装失败: {e}\n')
        sys.exit(1)

print('所有依赖安装完成！')