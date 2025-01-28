import black  # Test the importing of a non-stdlib module

# "Use" it without using it so linters don't complain
_ = black

def main():
    print("Hello from uv")


if __name__ == "__main__":
    main()
