# setup.py

from setuptools import setup, find_packages

setup(
    name='RAG-Voice-Assistance',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'speechrecognition',
        'pygame',
        'openai',
        'groq',
        'deepgram-sdk',
        'python-dotenv',
        'colorama',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'jarvis=run_voice_assistant:main'
        ]
    },
    author='nitesh-77',
    author_email='nitesh33lol@gmail.com',
    description='A modular voice assistant application with support for multiple state-of-the-art  AI models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nitesh-77',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    python_requires='>=3.10',
    include_package_data=True,
)
