import sys


class PrintUtil:
    _inplace = False

    @staticmethod
    def print_inplace(*text, **kwargs):
        """Print text by overwriting current line in terminal"""
        PrintUtil._inplace = True
        # Clear line
        print('\r', 79*' ', end='', **kwargs)
        sys.stdout.flush()

        # Update with new values
        print('\r', *text, end='', **kwargs)
        sys.stdout.flush()

    @staticmethod
    def print_normally(*text, **kwargs):
        """Print text on a new line"""
        if PrintUtil._inplace:
            print()
            PrintUtil._inplace = False
        print(*text, **kwargs)
