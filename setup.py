from setuptools import setup

setup(name = 'ecabc',
version = "1.1.1.dev2",
description = 'Artificial bee colony for parameters tuning based on fitness scores',
long_description = 'minor quality of life changes',
long_description_content_type = 'text/plain',
url = 'https://github.com/hgromer/Artificial-Bee-Colony',
author = 'Hernan Gelaf-Romer',
author_email = 'Hernan_Gelafromer@student.uml.edu',
license = 'MIT',
packages = ['ecabc'],
install_requires = ["numpy"],
zip_safe = False)
