from lexer import Lexer

source_code = "int main(void) {\r\n    return 10;\r\n}\r\n"

lexer = Lexer(source_code)
tokens = lexer.tokenize()

print("========== CRLF TEST ==========")

for token in tokens:
    print(
        f"Type: {token.kind.name:<15} "
        f"Value: {token.lexeme:<10} "
        f"Line: {token.line} "
        f"Column: {token.column}"
    )

print("========== TEST COMPLETED ==========")