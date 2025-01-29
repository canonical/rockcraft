# Test the importing of a non-stdlib module
import black  # pyright: ignore[reportMissingImports]

# "Use" it without using it so linters don't complain
_ = black


def main():
    print("Hello from uv")


if __name__ == "__main__":
    main()
