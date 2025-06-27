from setuptools import setup, find_packages

setup(
    name="goblintools",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "patool",
        "rarfile",
        "boto3",
        "opencv-python-headless",
        "numpy",
        "pdf2image",
        "pypdf",
        "beautifulsoup4",
        "striprtf",
        "dbfread",
        "python-docx",
        "python-pptx",
        "openpyxl",
        "xlrd",
        "odfpy",
        "textract",
        "unidecode",
        "pytesseract",
        "scipy",
        "pillow"
    ],
    author="Gean Matos",
    author_email="gean@webgoal.com.br",
    description="Toolkit for archive extraction, OCR parsing, and file text extraction",
    license="MIT",
    include_package_data=True,
)
