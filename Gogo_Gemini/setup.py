from setuptools import setup, find_packages

setup(
    name='gogo_gemini',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'google-generativeai',
        'python-dotenv'
    ],
    description='A package for interacting with the Gemini model',
    author='Harold E Lightfoot',
    url='https://github.com/HaroldELight/gogo_gemini',
    license='MIT',
)