import os
import subprocess


def parse_dependency_string(input_string):
    lines = input_string.strip().split("\n")
    result = {}
    current_package = None
    indentation_levels = {}

    for line in lines:
        parts = line.split(" ", 1)
        package_name = parts[0]

        indentation = line.index(package_name)
        indentation_levels[package_name] = indentation

        if indentation == 0:
            result[package_name] = {"name": package_name}
            current_package = package_name
        else:
            parent_package = next(
                parent for parent, level in indentation_levels.items() if level < indentation
            )
            if parent_package not in result:
                result[parent_package] = []
            result[parent_package].append({"name": package_name})

    return result


# Example input string (same as before)
input_string = """
click 8.1.6 Composable command line interface toolkit
└── colorama *
pytest 7.4.0 pytest: simple powerful testing with Python
├── colorama *
├── exceptiongroup >=1.0.0rc8
├── iniconfig *
├── packaging *
├── pluggy >=0.12,<2.0
└── tomli >=1.0.0
requests 2.31.0 Python HTTP for Humans.
├── certifi >=2017.4.17
├── charset-normalizer >=2,<4
├── idna >=2.5,<4
└── urllib3 >=1.21.1,<3
rich 13.5.2 Render rich text, tables, progress bars, syntax highlighting, markdown and more to the terminal
├── markdown-it-py >=2.2.0
│   └── mdurl >=0.1,<1.0
└── pygments >=2.13.0,<3.0.0
rich-click 1.6.1 Format click help output nicely with rich
├── click >=7
│   └── colorama *
└── rich >=10.7.0
    ├── markdown-it-py >=2.2.0
    │   └── mdurl >=0.1,<1.0
    └── pygments >=2.13.0,<3.0.0
"""


def get_dependencies(path: str = None) -> str:
    cmd = ["poetry", "show", "--tree"]
    if not path:
        path = os.curdir
    output = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path,
                            encoding="latin-1")
    if output.returncode != 0:
        raise ValueError(f'Error while getting a poetry tree. {output.stderr}')
    return output.stdout


if __name__ == '__main__':
    parsed_data = parse_dependency_string(input_string)
    print(parsed_data)
