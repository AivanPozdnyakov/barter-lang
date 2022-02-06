class BarterSyntaxError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CompileTimeError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class RunTimeError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def main() -> None:
    try:
        e = Exception(1, "ss")
        raise e #CompileTimeError("hahah")
    except BarterSyntaxError as e:
        print(e)
    except RunTimeError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
