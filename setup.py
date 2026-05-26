from setuptools import setup, find_packages

setup(
    name="nexvoid",
    version="1.0.0",
    description="Nexvoid: A Modern Language for Systems, Automation, Scripting & Cybersecurity",
    author="Nexvoid Lab",
    author_email="nexvoidcybertech@gmail.com",
    url="https://github.com/nexvoid-lab/nexvoid",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'nexvoid=bin.nexvoid:main',
        ],
    },
    python_requires=">=3.8",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Security",
    ],
)



