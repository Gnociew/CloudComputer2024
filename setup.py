from setuptools import setup, find_packages

setup(
    name="shuwa",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-cors',
        'opencv-python',
        'numpy',
        'tensorflow-macos',
        'tensorflow-metal',
        'mediapipe'
    ]
) 