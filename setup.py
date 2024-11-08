from setuptools import setup, find_packages

setup(
    name="NFT_Generation_Project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Load dependencies from requirements.txt
        "pip",
        "wheel"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "run_app=app:main"  # Command to run the app
        ]
    },
)