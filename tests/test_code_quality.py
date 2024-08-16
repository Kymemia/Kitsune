""" Module to test code quality of Python files in the project.
it tests: PEP8 compliance,
          Flake8 compliance,
          docstring compliance,
          and static typing.
"""
import ast
import os
import subprocess
from typing import List

# Constants
CODE_DIR: str = './'  # Change this to the dir containing code files


def validate_file(root: str, files: List[str]) -> List[str]:
    """
    It checks, validates and returns
    Python files in  a given dir recursively.
    Example:
    ---------
        a) python_files = validate_file(
            './',
            ['file1.py', 'file2.py', 'ToDo']
            ):

             => returns ['file1.py', 'file2.py']
        -----
         example above will return a list of python files
    """
    ignored_pyfiles = ["__init__.py"]
    python_files = []

    for file in files:
        file_path = os.path.join(root, file)
        if file.endswith('.py'):
            if file in ignored_pyfiles and \
                    os.path.getsize(file_path) == 0:
                continue
            python_files.append(file_path)
    return python_files


def get_python_files(directory: str) -> List[str]:
    """
    Retrieves a list of all Python
    files in the given directory,
    Example:
    --------
    if './' contains 'file1.py', 'file2.py', 'ToDo':
    a) python_files = get_python_files('./')
       `a)` will return ['file1.py', 'file2.py']
    """
    validated_python_files = []
    for root, _, files in os.walk(directory):
        if '__pycache__' in root:
            continue
        validated_python_files.extend(validate_file(root, files))
    return validated_python_files


def test_code_compliance() -> None:
    """Test that the code is PEP8 and Flake8 compliant.
    Example:
    ---------
    if pyfile has trailing whitespaces
    or a line longer than 79 characters,
        it will raise an assertion error
    """
    python_files = get_python_files(CODE_DIR)
    for file in python_files:
        for tool in ['pycodestyle', 'flake8']:
            result = subprocess.run(
                [tool, file],
                capture_output=True,
                text=True,
                check=False
            )
            assert result.returncode == 0, (
                f"{tool} violations found in {file}:\n{result.stdout}"
            )


def check_module_docstring(file: str, tree: ast.Module) -> None:
    """Check if the module-level
    docstring is at least 15 characters.
    Example:
    ---------
    if pyfile has a module docstring
    of less than 15 characters,
        it will raise an assertion error
    """
    module_docstring = ast.get_docstring(tree)
    assert (
        module_docstring is not None and len(module_docstring) >= 15
    ), (
        "Module-level docstring of at least "
        f"15 characters required in {file}"
    )


def check_class_function_docstring(
    file: str,
        tree: ast.Module) -> None:
    """Check if each class and function
    has a docstring of at least 15 characters.
    Example:
    --------
        if a class does not have
        a docstring or a short docstring,
        it will raise an assertion error
    """
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            assert docstring is not None and len(docstring) >= 15, (
                f"Docstring of at least 15 characters required in "
                f"{file} at line {node.lineno}"
            )
            if isinstance(node, ast.FunctionDef):
                assert 'Example' in docstring, (
                    f"Docstring in function {node.name} in {file} must"
                    f" contain an example"
                )


def test_docstring_compliance() -> None:
    """Test that each module, class,
    and function has a docstring of at least
    15 characters.
    Example:
    ---------
    if pyfile has a module docstring
    of less than 15 characters,
        it will raise an assertion error
    """
    python_files = get_python_files(CODE_DIR)
    for file in python_files:
        with open(file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

            check_module_docstring(file, tree)
            check_class_function_docstring(file, tree)


def check_function_annotations(
    node: ast.FunctionDef,
        file: str) -> None:
    """Check that each function argument
    and return type is statically typed.
    Example:
    --------
    def add(a: int, b: int) -> int:
    """
    # Functions to ignore
    function_exceptions: List[str] = ["__init__"]
    # arguments to ignore
    argument_exceptions: List[str] = ['self', 'cls']

    for arg in node.args.args:
        if node.name in function_exceptions or \
                arg.arg in argument_exceptions:
            continue
        assert arg.annotation is not None, (
            f"Argument {arg.arg} in "
            f"function {node.name} in {file} must "
            f"be statically typed"
        )
    assert node.returns is not None, (
        f"Return type in function `{node.name}` "
        f"in {file} must be statically typed"
    )


def check_variable_annotations(node: ast.AnnAssign, file: str) -> None:
    """Check that each
    variable is statically typed.
    Example:
    --------
    a: int = 10
    """
    target = node.target
    if isinstance(target, ast.Name):
        var_name = target.id
    elif isinstance(target, ast.Attribute):
        var_name = target.attr
    else:
        var_name = None
    assert (
        var_name is not None and node.annotation is not None
    ), (
        f"Variable {var_name} in {file} at "
        f"line {getattr(node, 'lineno', 'unknown')} "
        f"must be statically typed"
    )


def test_static_typing() -> None:
    """Test that each function and variable
    is statically typed.
    Example:
    ---------
    a: int = 10
    b: int = 20
    def add(a: int, b: int) -> int:
    """
    python_files = get_python_files(CODE_DIR)
    for file in python_files:
        with open(file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    check_function_annotations(node, file)
                if isinstance(node, ast.AnnAssign):
                    check_variable_annotations(node, file)
