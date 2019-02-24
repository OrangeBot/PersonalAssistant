from dev.test.test_imports.package_1 import process_string
from dev.test.test_imports.package_2 import method_2


def main():
    print("Launching runnable component. Result:")
    print(process_string(method_2()))


if __name__ == '__main__':
    main()
