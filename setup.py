from setuptools import setup

setup(name = 'ecabc',
version = "1.2.0",
description = 'Artificial bee colony for parameters tuning based on fitness scores',
long_description = 'settings revamp, bug fixes, algorithm changes',
long_description_content_type = 'text/plain',
url = 'https://github.com/ECRL/ecabc',
author = 'Hernan Gelaf-Romer',
author_email = 'Hernan_Gelafromer@student.uml.edu',
license = 'MIT',
packages = ['ecabc'],
install_requires = ["numpy"],
zip_safe = False)
