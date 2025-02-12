import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='reliza',
    version='0.1.0',
    author='haru+familiarbreakfast',
    description='A versatile framework to build open-domain conversational AI.',
    long_description='A fork of Eliza targeted for use with reddit. Sponsored by Theseus.',
    long_description_content_type='text/markdown',
    url='https://github.com/familiarbreakfast/reliza',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)