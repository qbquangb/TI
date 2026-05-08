import io
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thuonglib',
    version='1.0.8',
    author='Trần Đình Thương',
    author_email='qbquangbinh@gmail.com',
    # url='https://github.com/qbquangb/thuonglib',
    url='https://github.com/qbquangb/TI',
    description=' Utility by Tran Dinh Thuong',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.10.6'
)

'''
1. python setup.py sdist bdist_wheel
2. python -m twine upload --repository testpypi dist/*
   python -m twine upload dist/*
   python -m twine upload --skip-existing dist/*
3. pip install --index-url https://test.pypi.org/simple/ my-package
   pip install thuonglib
   pip install --no-cache-dir thuonglib
'''
