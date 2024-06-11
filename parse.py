from lexer import Token
from lexer import Lexer
from pprint import pprint
import random


class MakeTokenizer(Token):
    "处理token的基类"

    def __init__(self, tokens) -> None:
        self.pos = -1
        self.cur = None
        self.tokens = tokens
        self.tokensNum = len(tokens)

    def next(self):
        "移动游标至下一个token并返回当前token"
        t = self.cur
        self.pos += 1

        if self.pos >= self.tokensNum:
            self.cur = ["eof"]
        else:
            self.cur = self.tokens[self.pos]

        return t

    def peek(self, offset=0):
        "取出当前的值 + 偏移"
        if self.pos + offset >= self.tokensNum:
            return "eof"
        else:
            return Token.tk_type(self.tokens[self.pos + offset])

    def match(self, *m):
        "匹配字符 m"
        if self.peek() not in m:
            raise Exception(f"except {m}, but {self.peek()}")
        return self.next()


class Polistar(MakeTokenizer):
    "Cilly 文法解析器"

    def __init__(self, tokens) -> None:
        super().__init__(tokens)

    # 表达式处理部分
    def term(self):
        "解析表达式中的术语"
        curr = self.peek()
        # 处理调用函数嵌套
        if curr == "id":
            t = self.next()
            if self.peek() == "(":
                return self.func_call(t)
            else:
                return self.assign_stat(t)

        # 处理负数
        if self.peek() == "-":
            self.next()
            if self.peek() == "num":
                t = self.next()
                return ["num", -t[1]]

        if self.peek() == "num" or self.peek() == "str" or self.peek() == "bool":
            return self.next()

        if self.peek() == "(":
            tmp = ()
            self.match("(")
            while self.peek() != ")":
                if self.peek() == ",":
                    self.match(",")
                e = self.expr()
                tmp.append(e)
            self.match(")")
            return e

        if self.peek() == "fun":
            return self.fun_def()
        elif self.peek() == "var":
            return self.var_decl()
        elif self.peek() == "print":
            return self.print_stat()
        elif self.peek() == "random":
            return self.randomImpl()
        elif self.peek() == "=":
            return self.var_decl()
        elif self.peek() == "eof":
            return None
        else:
            raise Exception(f"unexpected token: {self.peek()}")

    def add_sub(self):
        e = self.term()
        while self.peek() in ["+", "-", "*", "/"]:
            op = self.peek()
            self.match(op)
            e = [op, e, self.term()]
            if self.peek() == "!":
                self.match("!")
                e = ["!", e]
        return e

    def comparison(self):
        e = self.add_sub()
        while self.peek() in [">", ">=", "<", "<="]:
            op = self.peek()
            self.match(op)
            e = [op, e, self.term()]
        return e

    def equality(self):
        e = self.comparison()
        while self.peek() in ["==", "!="]:
            op = self.peek()
            self.match(op)
            e = [op, e, self.comparison()]
        return e

    def logic_and(self):
        e = self.equality()
        while self.peek() == "and":
            self.match("and")
            e = ["and", e, self.equality()]
        return e

    def logic_or(self):
        e = self.logic_and()
        while self.peek() == "or":
            self.match("or")
            e = ["or", e, self.logic_and()]
        return e

    def expr(self):
        return self.logic_or()

    def fun_def(self):
        "匹配函数定义"
        self.match("fun")
        name = self.match("id")
        # 参数捕获
        self.match("(")
        params = []
        while self.peek() != ")":
            params.append(self.match("id"))
            if self.peek() == ",":
                self.match(",")
        self.match(")")
        # 方法体开始
        self.match("{")
        body = []
        while self.peek() != "}":
            # 递归判断
            body.append(self.statement())
        self.match("}")
        return ["fun_def", name, params, body]

    def var_decl(self):
        "匹配变量声明和赋值"
        self.match("var")
        name = self.match("id")
        if self.peek() == "=":
            self.match("=")
            value = self.statement()
        else:
            value = None
        return ["var_decl", name, value]

    # 处理设置画笔参数
    def setValue(self):
        "匹配设置画笔变量"
        self.match("set")
        name = self.match("id")
        keyword = Token.tk_val(name)
        t = []

        # 设置画笔颜色
        if keyword == "color":
            val = self.statement()
            return ["set_value", name, val]
        # 设置初始点
        elif keyword == "xy":
            self.match("(")
            while self.peek() != ")":
                if self.peek() == ",":
                    self.match(",")
                t.append(self.next())
            self.match(")")
            return ["set_value", name] + t
        # 设置画笔粗细
        elif keyword == "width":
            val = self.statement()
            return ["set_value", name, val]
        # 设置是否显示轨迹
        elif keyword == "tracer":
            val = self.statement()
            return ["set_value", name, val]

        else:
            raise Exception("unkown turtle's value {}".format(keyword))

    def assign_or_func(self):
        "判断是赋值还是函数调用"
        t = self.next()
        if self.peek() == "(":
            return self.func_call(t)
        else:
            return self.assign_stat(t)

    def assign_stat(self, name=None):
        "无 var 声明情况下赋值"
        if name is None:
            name = self.match("id")
        # 赋值的情况
        if self.peek() == "=":
            self.match("=")
            value = self.expr()
            return ["assign_stat", name, value]
        # 调用变量的情况
        else:
            return ["use_var", name]

    def func_call(self, name=None):
        "匹配函数调用"
        if name == None:
            name = self.match("id")
        self.match("(")
        args = []
        while self.peek() != ")":
            if self.peek() == ",":
                self.match(",")
            args.append(self.statement())
        self.match(")")
        return ["func_call", name, args]

    def ret_stat(self):
        "匹配 return 语句"
        self.match("return")
        if self.peek() != ";":
            e = self.statement()
        else:
            e = None
        if self.peek() == ";":
            self.next()  # 跳过分号，这里只是一个空语句

        return ["return", e]

    def if_stat(self):
        "匹配 if 语句"
        self.match("if")
        self.match("(")
        cond = self.expr()
        self.match(")")
        # 可以为 if 添加花括号
        if self.peek() == "{":
            self.match("{")

        true_s = []
        false_s = []

        while self.peek() != "}":
            true_s.append(self.statement())

        self.match("}")

        # 处理 else 语句
        if self.peek() == "else":
            self.match("else")
            if self.peek() == "if":
                false_s = self.if_stat()
            else:
                self.match("{")
                while self.peek() != "}":
                    false_s.append(self.statement())
                self.match("}")
        else:
            false_s = None
        return ["if", cond, true_s, false_s]

    def while_stat(self):
        "匹配 while 循环"
        self.match("while")
        self.match("(")
        cond = self.expr()
        self.match(")")
        self.match("{")
        body = []
        while self.peek() != "}":
            body.append(self.statement())
        self.match("}")
        return ["while", cond, body]

    def for_stat(self):
        "处理for语句块"
        self.match("for")
        self.match("(")
        cond = []
        while self.peek() != ")":
            t = self.statement()
            if t is not None:
                cond.append(t)
        self.match(")")
        make_var, expr, fin = cond
        # 处理循环体
        self.match("{")
        body = []
        while self.peek() != "}":
            body.append(self.statement())
        self.match("}")
        return ["for", make_var, expr, fin, body]

    def print_stat(self):
        "解析打印语句"
        self.match("print")
        self.match("(")
        args = []
        while self.peek() != ")":
            # 处理多个参数的情况
            if self.peek() == ",":
                self.match(",")
            args.append(self.statement())
        self.match(")")
        return ["print", args]

    def randomImpl(self):
        "定义随机数生成函数"
        self.match("random")
        self.match("(")
        args = []
        while self.peek() != ")":
            # 处理多个参数的情况
            if self.peek() == ",":
                self.match(",")
            args.append(self.statement())
        self.match(")")
        return ["random", args]

    def forward(self):
        "处理forward 语句"
        self.match("forward")
        args = self.statement()
        return ["forward", args]

    def back(self):
        "处理back语句"
        self.match("back")
        args = self.statement()
        return ["back", args]

    def penup(self):
        "抬笔操作"
        self.match("penup")
        return ["penup"]

    def pendown(self):
        "落笔操作"
        self.match("pendown")
        return ["pendown"]

    def right(self):
        "向右转动角度"
        self.match("right")
        args = self.statement()
        return ["right", args]

    def left(self):
        "向左转动角度"
        self.match("left")
        args = self.statement()
        return ["left", args]

    def clear(self):
        "清空画布"
        self.match("clear")
        return ["clear"]

    def save(self):
        "保存至文件"
        self.match("save")
        args = self.statement()
        return ["save", args]

    def hide(self):
        "隐藏光标"
        self.match("hide")
        return ["hide"]
    
    def maintain(self):
        "保持turtle窗口打开"
        self.match("maintain")
        return ["maintain"]

    def circle(self):
        "绘制圆弧"
        self.match("circle")
        args = []
        while self.peek() == "num":
            args.append(self.next())
        return ["circle"] + args

    def statement(self):
        "代码块识别"
        curr = self.peek()
        if curr == "fun":
            return self.fun_def()
        elif curr == "var":
            return self.var_decl()
        elif curr == "set":
            return self.setValue()
        elif curr == "return":
            return self.ret_stat()
        elif curr == "if":
            return self.if_stat()
        elif curr == "while":
            return self.while_stat()
        elif curr == "for":
            return self.for_stat()

        elif curr == ";":
            self.next()
            return None  # 跳过分号，这里只是一个空语句
        elif curr == "forward":
            return self.forward()
        elif curr == "back":
            return self.back()
        elif curr == "penup":
            return self.penup()
        elif curr == "pendown":
            return self.pendown()
        elif curr == "left":
            return self.left()
        elif curr == "right":
            return self.right()
        elif curr == "clear":
            return self.clear()
        elif curr == "save":
            return self.save()
        elif curr == "circle":
            return self.circle()
        elif curr == "hide":
            return self.hide()
        elif curr == "maintain":
            return self.maintain()
        return self.expr()

    def program(self):
        "匹配代码块"
        self.next()
        r = []
        while self.peek() != "eof":
            r.append(self.statement())
        return ["program", r]

    def parse(self):
        "执行解析"
        return self.program()


if __name__ == "__main__":
    prog = """
    for (var i = 1; i < 10; i = i+1) {
        print(i)
    }
    """

    parser = Polistar(Lexer(prog).parse())
    pprint(parser.parse())
