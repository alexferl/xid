from setuptools import setup

setup(
    name="python-xid",
    version="0.1.0",
    description="",
    url="http://github.com/alexferl/xid",
    author="Alexandre Ferland",
    author_email="aferlandqc@gmail.com",
    license="MIT",
    packages=["xid"],
    zip_safe=False,
    install_requires=[],
    setup_requires=["pytest-runner>=5.2"],
    tests_require=["pytest>=6.0.1"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
