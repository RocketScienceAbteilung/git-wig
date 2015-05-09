import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='gitwig',
        version='0.1',
        license='MIT',
        packages=setuptools.find_packages(),
        install_requires=[
            'numpy>=1.7',
            'mido',
            'isobar>=0.0.3',
            'watchdog',
        ],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
            ],
        },
        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Telecommunications Industry',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Information Analysis',
        ],

        entry_points={'console_scripts': [
            'git-wig=gitwig:main',
            'git-wig-ports=gitwig.utils:print_ports',
            'git-wig-messages=gitwig.utils:print_messages',
        ]},
    )
