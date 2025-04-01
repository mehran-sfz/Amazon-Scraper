from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="amazon_scraper",
    version="0.1.0",
    author="Mehran Safarzadeh",
    url="https://github.com/mehran-sfz/Amazon-Scraper",
    install_requires=[
        "beautifulsoup4>=4.13.3",
        "requests>=2.32.3",
        "pillow>=11.2.0",
        "selenium>=4.30.0",
    ],
    packages=find_packages(),
    
    long_description=long_description,
    long_description_content_type="text/markdown",
)
    