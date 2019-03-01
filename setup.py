from setuptools import setup

setup(name = 'ecabc',
version = "2.2.2",
description = 'Artificial bee colony for parameters tuning based on fitness scores',
url = 'https://github.com/ECRL/ecabc',
author = 'Sanskriti Sharma, Hernan Gelaf-Romer',
author_email = 'Sanskriti_Sharma@student.uml.edu, Hernan_Gelafromer@student.uml.edu',
license = 'MIT',
packages = ['ecabc'],
install_requires = ["numpy", "ColorLogging"],
zip_safe = False)
