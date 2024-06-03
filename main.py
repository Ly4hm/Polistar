import os
import turtle

from PIL import Image

from lexer import Lexer, Token
from parse import Polistar

# 初始化turtle
t = turtle.Turtle()
screen = turtle.Screen()
screen.colormode(255)


def hex_to_rgb(hex_color):
    # 移除十六进制颜色代码中的 '#'
    hex_color = hex_color.lstrip("#")
    # 将六位十六进制颜色代码转换为RGB格式
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return rgb


def evaluate_expression(expr):
    """Evaluate a simple arithmetic expression."""
    if expr[0] == "num" or expr[0] == "str":
        return expr[1]
    
    # 使用变量的情况
    elif expr[0] == "use_var":
        var_name = Token.tk_val(expr[1])
        return namespace[var_name]

    elif expr[0] == "tuple":  # 处理数组表达式
        return (evaluate_expression(expr[1]), evaluate_expression(expr[2]))

    elif isinstance(expr, list):
        operator = expr[0]

        left_operand = evaluate_expression(expr[1])
        right_operand = evaluate_expression(expr[2])
        if operator == "+":
            return left_operand + right_operand
        elif operator == "-":
            return left_operand - right_operand
        elif operator == "*":
            return left_operand * right_operand
        elif operator == "/":
            return left_operand / right_operand

    else:
        raise ValueError(f"Unsupported expression: {expr}")

# 定义全局变量范围
namespace = {}

def execute_command(command):
    """Execute a single turtle command."""
    cmd = Token.tk_type(command)
    args = command[1:]
    
    # 设置变量
    if cmd == "var_decl":
        key = Token.tk_val(args[0])
        val = evaluate_expression(args[1])
        namespace[key] = val
            
    
    # 设置画笔参数
    elif cmd == "set_value":
        attribute = Token.tk_val(args[0])

        if attribute == "color":
            value = evaluate_expression(args[1])
            if "#" in value:
                value = hex_to_rgb(value)
            t.color(value)
        elif attribute == "initial_point":
            t.penup()
            value1 = evaluate_expression(args[-2])
            value2 = evaluate_expression(args[-1])
            t.goto(value1, value2)
            t.pendown()
        elif attribute == "width":
            args = args[1:]
            pensize = evaluate_expression(args[0])
            t.pensize(pensize)
        else:
            raise ValueError(f"Unsupported attribute: {attribute}")

    # turtle 操作
    elif cmd == "forward":
        distance = evaluate_expression(args[0])
        t.forward(distance)
    elif cmd == "back":
        distance = evaluate_expression(args[0])
        t.back(distance)

    elif cmd == "left":
        angle = evaluate_expression(args[0])
        t.left(angle)
    elif cmd == "right":
        angle = evaluate_expression(args[0])
        t.right(angle)

    elif cmd == "penup":
        t.penup()
    elif cmd == "pendown":
        t.pendown()

    elif cmd == "save":
        canvas_width = 1000
        canvas_height = 1000

        t.getscreen().getcanvas().postscript(
            colormode="color",
            file="tmp.eps",
            pagewidth=canvas_width,
            pageheight=canvas_height,
            width=canvas_width,
            height=canvas_height,
            x=-canvas_width / 2,
            y=-canvas_height / 2,
        )

        im = Image.open("tmp.eps")
        im.save("1.jpg")
        im.close()
        os.remove("tmp.eps")

    elif cmd == "clear":
        t.clear()
    elif cmd == "hide":
        t.hideturtle()
        
    elif cmd == "circle":
        if len(args) == 2:
            t.circle(Token.tk_val(args[0]), Token.tk_val(args[1]))
        elif len(args) == 1:
            t.circle(Token.tk_val(args[0]))

    else:
        raise ValueError(f"Unsupported command: {cmd}")


def execute_program(program):
    """Execute a list of turtle commands."""
    for command in program[1]:
        execute_command(command)


if __name__ == "__main__":
    prog = """
    var a = -50
    var color = "yellow"
    # 设置画笔具体属性
    set color color
    set initial_point (-60,100)
    set width 10 + 1
    # 前进
    forward a
    left 60
    forward 50 * 2
    right 90
    # 抬笔
    penup
    forward 300
    pendown
    set color "#0a9d5b"
    forward 20
    left 150
    back 100
    set initial_point (0,0)
    forward 60
    set initial_point (0,0)
    circle 100
    set color "black"
    set initial_point (50,50)
    circle 100 120
    # 保存图片
    save "test.png"
    """


    polistar = Polistar(Lexer(prog).parse())

    tokens = [
        "program",
        [
            ["var_decl", ["id", "a"], ["str", "yellow"]],
            ["set_value", ["id", "color"], ["use_var", ["id", "a"]]],
            ["forward", ["num", 100]],
        ],
    ]

    execute_program(polistar.parse())
    # execute_program(tokens)

    # 保持窗口打开
    turtle.done()
