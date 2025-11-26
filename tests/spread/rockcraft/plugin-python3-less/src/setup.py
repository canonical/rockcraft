from distutils.core import setup  # pyright: ignore[reportMissingImports]

setup(
    name="hello",
    version="0.1",
    entry_points={"console_scripts": ["hello=hello.__main__:main"]},
    packages=["hello"],
)
