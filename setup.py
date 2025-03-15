from setuptools import setup, find_packages

setup(
    name="invoice_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",  # Ensure PyQt is included for the GUI
        "python-docx", 
        "docx2pdf"
    ],
    entry_points={
        "console_scripts": [
            "run-invoice=invoice_generator.invoice_generator:main",
        ],
    },
)
