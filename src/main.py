from lark import Lark


def main() -> None:
    with open("../res/bl_lexer_rules.txt", "r") as f:
        parser = Lark(f.read())
    with open("../res/examples/fib.barter", "r") as f:
        result = parser.parse(f.read())
    print(result.pretty())


if __name__ == '__main__':
    main()
