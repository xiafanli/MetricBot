import subprocess
import sys
import toml

# 读取pyproject.toml文件
with open('pyproject.toml', 'r') as f:
    pyproject = toml.load(f)

# 获取依赖列表
dependencies = pyproject['project']['dependencies']

print("开始安装依赖...")
for package in dependencies:
    print(f"正在安装: {package}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://mirrors.aliyun.com/pypi/simple/"])
    except subprocess.CalledProcessError as e:
        print(f"安装 {package} 失败: {e}")
        sys.exit(1)

print("所有依赖安装完成!")