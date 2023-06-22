from examer import Examer

exam_id = 75
exam_title = "“学悟新思想、奋进新征程”主题教育云答题竞赛（练习）"

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    exam = Examer("张三", "123456789012345678", exam_id, exam_title)
    exam.exam()
    pass
