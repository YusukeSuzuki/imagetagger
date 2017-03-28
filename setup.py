from setuptools import setup

setup(name='imagetagger',
    version='0.1.0',
    desctiption='GUI image tagging tool for mahine learning',
    author='Yusuke Suzuki',
    license='MIT',
    packages=['imagetagger'],
    entry_points={
        'console_scripts':[
            'imagetagger = imagetagger.main:run'
        ]
    },
    install_requires=[
        'PyQt5'
    ],
    zip_safe=False)


