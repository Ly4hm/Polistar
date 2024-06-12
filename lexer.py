class Token:
    "最基础的 Token 类"

    @staticmethod
    def make_tk(type, val=None) -> list:
        "生成指定的 token"
        return [type, val] if val!=None else [type]

    @staticmethod
    def tk_type(t):
        "返回指定token的类型"
        return t[0]

    @staticmethod
    def tk_val(lst):
        "返回指定token的值"
        if isinstance(lst[1], list):
            return Token.tk_val(lst[1])
        
        while len(lst) == 1:
            lst = lst[0]
        return lst[1]


class Lexer():
    "解析程序生成tokens"
    # 静态变量
    keywords = [
        "return",
        "fun",
        "print",
        "if",
        "else",
        "var",
        "true",
        "false",
        "while",
        "for",
        "repeat",
        "in",
        "range",
        "penup",
        "pendown",
        "left",
        "right",
        "forward",
        "back",
        "set",
        "save",
        "clear",
        "hide",
        "circle",
        "random",
        "maintain",
        "beginfill",
        "endfill"
    ]
    blank_lst = [" ", "\t", "\r", "\n"]
    symbols = [",", ":", "+", "-", "*", "/", ";", "(", ")", "{", "}", "[", "]"]

    def __init__(self, prog):
        self.pos = -1
        self.cur = None
        self.prog = prog

    def parse(self):
        # 解析程序
        self.next()
        tokens = []
        while True:
            t = self.token()
            # 去除注释
            if not t:
                continue

            tokens.append(t)
            # 程序结束
            if Token.tk_type(t) == "eof":
                break

        return tokens

    def error(src, msg):
        raise Exception(f"<{src}>: {msg}")

    def err(self, msg):
        "属于 Lexer 的简化版 err"
        self.error("Lexer", msg)

    def next(self):
        "移动游标并返回当前值"
        t = self.cur
        self.pos += 1
        # 边界检测
        if self.pos >= len(self.prog):
            self.cur = "eof"
        else:
            self.cur = self.prog[self.pos]

        return t

    def peek(self):
        "返回当前值"
        return self.cur

    def match(self, m):
        "强制匹配一个字符"
        if self.cur != m:
            self.err(f"except {m}, but {self.cur}")

        return self.next()

    def ws_skip(self):
        "跳过空白字符"
        while self.peek() in Lexer.blank_lst:
            self.next()

    def is_string(self):
        "匹配字符串"
        self.match('"')
        r = ""
        # 遍历字符部分
        while self.peek() != '"':
            r = r + self.next()
        self.match('"')

        return Token.make_tk("str", r)

    @staticmethod
    def isdigit(c):
        "判断字符是否为数字"
        return c >= "0" and c <= "9"

    @staticmethod
    def isletter_(c):
        return c == "_" or (c >= "a" and c <= "z") or (c >= "A" and c <= "Z")

    @staticmethod
    def isletter_or_digit(c):
        return Lexer.isdigit(c) or Lexer.isletter_(c)

    def num(self):
        "匹配数字"
        r = self.next()

        while Lexer.isdigit(self.peek()):
            r = r + self.next()

        if self.peek() == ".":
            r = r + self.next()
            while Lexer.isdigit(self.peek()):
                r = r + self.next()

        val = float(r) if "." in r else int(r)

        return Token.make_tk("num", val)

    def id(self):
        "匹配 id"
        r = self.next()

        while Lexer.isletter_or_digit(self.peek()):
            r = r + self.next()

        # 处理关键字
        if r in Lexer.keywords:
            return Token.make_tk(r)
        # 处理bool值
        elif r == "False" or r == "True":
            return Token.make_tk("bool", r)

        return Token.make_tk("id", r)

    def token(self):
        self.ws_skip()

        t = self.peek()

        if t == "eof":
            return Token.make_tk("eof")

        elif t in Lexer.symbols:
            self.next()
            return Token.make_tk(t)

        elif t == "=":
            self.next()
            if self.peek() == "=":
                self.next()
                return Token.make_tk("==")
            else:
                return Token.make_tk("=")

        elif t == ">":
            self.next()
            if self.peek() == "=":
                self.next()
                return Token.make_tk(">=")
            else:
                return Token.make_tk(">")

        elif t == "<":
            self.next()
            if self.peek() == "=":
                self.next()
                return Token.make_tk("<=")
            else:
                return Token.make_tk("<")

        elif t == "!":
            self.next()
            if self.peek() == "=":
                self.next()
                return Token.make_tk("!=")
            # 阶乘
            else:
                return Token.make_tk("!")

        elif t == '"':
            return self.is_string()

        elif Lexer.isdigit(t):
            return self.num()

        elif Lexer.isletter_(t):
            return self.id()

        # 去除注释
        elif t == "#":
            curr = self.next()
            while curr != "\n":
                curr = self.next()
            return None

        self.err(f"非法字符 {t}")


if __name__ == "__main__":
    prog = """
    beginfill "red"
    
    for (var i = 1; i < 5; var i = i + 1) {
        forward 100
        left 90
    }
    
    endfill
    """

    lexer = Lexer(prog)
    print(lexer.parse())
