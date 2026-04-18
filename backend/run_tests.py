import sys
sys.path.insert(0, 'E:\\code\\PrometheusBot\\backend')

from venv.Scripts import pytest

if __name__ == '__main__':
    sys.exit(pytest.main(['-v', 'tests/test_simple.py']))
