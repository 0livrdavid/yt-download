from setuptools import setup


setup(
    name="yt-download",
    version="1.2.1",
    author="David Oliveira",
    author_email="olivr.david@gmail.com",
    description="A simple CLI tool to download YouTube videos and playlists in multiple audio formats",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.10",
    packages=["yt_download"],
    install_requires=[
        "yt-dlp>=2023.1.6",
        "colorama>=0.4.6",
        "rich>=13.0.0",
        "requests>=2.28.0",
        "urllib3<2",
    ],
    entry_points={
        "console_scripts": [
            "yt-download=yt_download.main:main",
        ]
    },
    project_urls={
        "Homepage": "https://github.com/0livrdavid/yt-download",
        "Repository": "https://github.com/0livrdavid/yt-download",
        "Bug Reports": "https://github.com/0livrdavid/yt-download/issues",
    },
)
