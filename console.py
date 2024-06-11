import os
import argparse
import turtle

from main import Polistar, execute_program
from lexer import Lexer


# 解析器设置
parser = argparse.ArgumentParser(
    prog="Polistar",
    description="A variant implementation of logo language",
    epilog="Useage: console.py 1.star",
)

parser.add_argument("filename", nargs="?", default=None)  # 绘图的程序

args = parser.parse_args()


# 解析参数调用解释器
# 文件输入模式
filename = args.filename
if filename is not None:
    with open(filename, "r" ,encoding="utf-8") as code_file:
        code = code_file.read() + "\n"
        polistar = Polistar(Lexer(code).parse())
        execute_program(polistar.parse())
