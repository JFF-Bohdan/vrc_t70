from setuptools import find_packages, setup

from vrc_t70 import __version__

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

PACKAGE_NAME = "vrc_t70"

README_FILE = "README.md"
install_reqs = parse_requirements("requirements.txt", session=False)

try:
    requirements = [str(ir.req) for ir in install_reqs]
except:
    requirements = [str(ir.requirement) for ir in install_reqs]


hyphen_package_name = PACKAGE_NAME.replace("_", "-")


def read_file_content(file_name):
    with open(file_name) as f:
        return f.read()


if __name__ == "__main__":
    packages_to_remove = ["tests"]
    packages = find_packages()

    for item in packages_to_remove:
        if item in packages:
            packages.remove(item)

    setup(
        name=PACKAGE_NAME,
        version=__version__,
        author="Bohdan Danishevsky",
        author_email="dbn@aminis.com.ua",
        license="MIT",
        description="Module to support VRC-T70 hardware",
        long_description="Please read https://github.com/JFF-Bohdan/vrc_t70/blob/master/README.md for information",
        keywords=["VRC-T70", "thermo sensors", "DS18B20"],
        url="http://github.com/JFF-Bohdan/vrc_t70",
        platforms="all",
        classifiers=[],
        packages=packages,
        install_requires=requirements,
        zip_safe=False,
        entry_points={
            "console_scripts": [
                "find_devices=vrc_t70.command_line.find_devices:main",
                "get_temperatures=vrc_t70.command_line.get_temperatures:main",
                "vrc-t70=vrc_t70.cli_tools.cli:cli",
            ],
        }
    )
