import subprocess
from setuptools import setup, find_packages

xmi2conll_version = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="xmi2conll",
    version=xmi2conll_version,
    author='Lucas Terriel',
    license='MIT',
    description='Simple CLI to convert any annotated document in UIMA CAS XMI to CONLL format (IOB schema support).',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Lucaterre/xmi2conll',
    py_modules=['x2c', 'src'],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires='>=3.7',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        x2c=x2c:main
    """
)
