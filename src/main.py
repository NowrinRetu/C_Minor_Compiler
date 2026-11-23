
import argparse
import sys

from lexer import Lexer
from diagnostics import LexerError


def main():

    parser = argparse.ArgumentParser(
        description="C Minor Compiler"
    )

    parser.add_argument(
        "source",
        help="C Minor source file"
    )

    parser.add_argument(
        "--dump-tokens",
        action="store_true",
        help="Display lexer tokens"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check source file for lexical errors"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="C Minor Compiler Version 1.0"
    )

    args = parser.parse_args()

    try:
        with open(args.source, "r", encoding="utf-8") as file:
            source_code = file.read()

        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        if args.dump_tokens:
            for token in tokens:
                print(
                    f"Type: {token.kind.name:<15} "
                    f"Value: {token.lexeme:<10} "
                    f"Line: {token.line} "
                    f"Column: {token.column}"
                )

        elif args.check:
            print("Lexical analysis successful.")
            print("No lexical errors found.")

    except LexerError as error:
        print(error)
        sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File '{args.source}' not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
