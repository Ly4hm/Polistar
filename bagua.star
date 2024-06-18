# 定义一系列常量
## 卦象内单元常量
var SHORT_LINE = 20
var INTERVAL_LENGTH = 15
var PEN_WIDTH = 7
var LINE_INTERVAL = 20
var DISTANCE = 70
var SUM = SHORT_LINE * 2 + 15

## 外框常量
var MARGIN_LENGTH = 200
var MARGIN_WIDTH = 2
var SQRT2 = 1.4142135623730951

# 绘制卦象两短线
fun two() {
    set width PEN_WIDTH
    hide
    forward SHORT_LINE
    penup
    forward INTERVAL_LENGTH
    pendown
    forward SHORT_LINE
}

# 绘制卦象单横线
fun one() {
    set width PEN_WIDTH
    hide
    forward SHORT_LINE * 2 + 15
}

# 下移并复位
fun down_and_reset() {
    hide
    right 90
    penup
    forward LINE_INTERVAL
    right 90
    forward SHORT_LINE * 2 + 15
    pendown
    right 180
}

# 随机绘制一个卦象单元
fun draw_cell() {
    # 定义临时变量
    var len_one = 0
    var len_two = 0

    for (var i = 1; i < 4; var i = i + 1) {
        var t = random(0,2)

        # 判断绘制双短线还是单线
        if (t > 1) {
            # 用来控制数量相同
            if (len_two > 0) {
                one()
            } else {
                var len_two = len_two + 1
                two()
            }
        } else {
            if (len_one > 0) {
                two()
            } else {
                var len_one = len_one + 1
                one()
            }
        }
        # 复位
        down_and_reset()
    }
}

# 保存移动至内部绘制卦象
fun stored_move(mode) {
    penup
    if (mode == 0) {
        left 90
        forward DISTANCE
        left 90
        forward MARGIN_LENGTH / 2
        forward SUM / 2
        left 180
    } else {
        left 90
        forward LINE_INTERVAL * 3
        left 90
        back SUM / 2
        back MARGIN_LENGTH / 2
        left 90
        forward DISTANCE
        left 90
    }
    pendown
}



# 开始绘制
set tracer True

## 进入初始位置
penup
right 90
forward SQRT2 / 2 * MARGIN_LENGTH + MARGIN_LENGTH / 2 + 50
left 90
forward MARGIN_LENGTH / 2
pendown

## 绘制边框
repeat 9 {
    left 45
    set width MARGIN_WIDTH
    forward MARGIN_LENGTH

    ## 绘制内部卦象
    stored_move(0)
    draw_cell()
    stored_move(1)
}

## 绘制内部圆形
set xy (50,50)
circle 100 100
forward 100

## 后处理
save "tmp.png"
maintain
