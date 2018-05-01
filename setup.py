from setuptools import setup

long_description = "Added support for maximizing a fitness function rather than minimizing it through the abc.specifyMinOrMax('max') function. Employer bees now reset if after an x amount of iterations the best fitness score has not improved."

setup(name = 'ecabc',
version = "1.1.0.dev1",
description = 'Artificial bee colony for parameters tuning based on fitness scores',
long_description = long_description,
long_description_content_type = 'text/plain',
url = 'https://github.com/hgromer/Artificial-Bee-Colony',
author = 'Hernan Gelaf-Romer',
author_email = 'Hernan_Gelafromer@student.uml.edu',
license = 'MIT',
packages = ['ecabc'],
install_requires = ["numpy"],
zip_safe = False)
