#导入模块以及定义变量
import time
import random
import re
import shutil
import unicodedata
import pprint as p
from Q_A import *
crazy_n = 0
is_crazy = False
v = 1.3
last_say = []

#定义函数
def char_print(text,end = ''):
    '''逐字输出，默认不换行，end里写结尾的输出内容'''
    if BUSY_A[4] in text:
        for t in text:
            if t == " ":
                time.sleep(1)
            else:
                print(t, end='', flush=True)
                time.sleep(0.05)
        return None
    for t in text:
        print(t, end='', flush=True)
        time.sleep(0.05)
    print(end, end='', flush=True)

def display_width(text):
    width = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def clean_float_result(result):
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return (f"{result:.10f}").rstrip('0').rstrip('.')

def pysum(s):
    '''用eval计算算式的结果并返回'''
    if len(s) < 41:
        try:
            num = eval(s)
            num = clean_float_result(num)
            return f"答案是：{num}"
        except:
            return "俺不鸡道怎么算w(ﾟДﾟ)w"
    else:
        return "算式太长了,俺拒绝计算🤪!"

def clear_input_lines(text, prompt):
    columns = shutil.get_terminal_size((80, 20)).columns
    total_width = display_width(prompt) + display_width(text)
    lines = max(1, (total_width + columns - 1) // columns)
    for _ in range(lines):
        print("\033[F\033[2K", end='')

def think_over():
    for i in range(5):
        t = '.' * (i + 1)
        print(f"\033[34m正在思考中{t}\033[0m", end = '\r')
        time.sleep(0.4)
    print('\r               ', end = '\r')

def answer(question):
    global is_crazy
    if "速算" in question or "挑战" in question or "数学" in question:
        play_math_challenge()
        return None
    if "石头剪刀布" in question or "猜拳" in question:
        play_rqs()
        return None
    if "猜数字" in question:
        play_guess_n()
        return None
    if "游戏" in question:
        if random.randint(0,1) == 0:
            play_rqs()
            return None
        else:
            play_guess_n()
            return None
    if "发疯" in question or "疯狂" in question:
        think_over()
        if not is_crazy:
            is_crazy = True
            char_print("\033[36m🤖:如你所愿！我要疯了……哇哩哇哩哇！你好！我是疯狂戴夫！\033[0m\n")
        else:
            char_print("\033[36m🤖:你说什么?告诉你，我已经疯狂了👾!\033[0m\n")
        return None
    if "恢复" in question:
        think_over()
        if is_crazy:
            is_crazy = False
            char_print("\033[34m🤖:好!这就恢复正常👋\033[0m\n")
        else:
            char_print("\033[34m🤖:你在说啥?我很正常啊🤔\033[0m\n")
        return None
    c = become_crazy()
    if c == None:
        try:
            question = question.replace("=","").replace("?","").replace("!","").replace(" ","").replace("？","").replace("！","")
            question = question.replace("等于","").replace("几","")
        except:
            pass
        if "刚刚" in question or "之前" in question or "刚才" in question:
            if not last_say == []:
                return f"刚才你问：“{last_say[0]}”，我回答：“{last_say[1]}”"
            else:
                return "我们还什么都没聊呢🧐"
        if re.search(r"\d+[+\-*/]\d+",question):
            return pysum(question)
        for q in Q_A:
            if re.search(r"^\s*$",question):
                return random.choice(Q_A["not have"])
            if isinstance(Q_A[q],dict):
                if q in question:
                    for t in Q_A[q]:
                        if t in question:
                            return random.choice(Q_A[q][t])
            elif q in question:
                return random.choice(Q_A[q])
        return random.choice(BUSY_A)
    else:
        return c

#游戏函数
def play_rqs():
        c_not_win = 0
        p_not_win = 0
        think_over()
        char_print("\033[34m🤖:好嘞，石头剪刀布游戏开始!\n")
        while True:
            random_choice=random.randint(0,2)

            if random_choice==0:
                computer_choice='石头'
            elif random_choice==1:
                computer_choice='剪刀'
            else:
                computer_choice='布'

            char_print('\033[34m   你出石头、剪刀还是布？')
            user_choice=input('')
            while user_choice!='石头'and user_choice!='剪刀'and user_choice!='布':
                char_print('   请重新输入！你出石头、剪刀还是布？')
                user_choice=input('')

            char_print(f'   你出：{user_choice},我出：{computer_choice}\n')
            time.sleep(1)

            if computer_choice==user_choice:
                winner='平局'
            elif computer_choice=='布'and user_choice=='石头':
                winner='我'
                p_not_win += 1
                c_not_win = 0
            elif computer_choice=='石头'and user_choice=='剪刀':
                winner='我'
                p_not_win += 1
                c_not_win = 0
            elif computer_choice=='剪刀'and user_choice=='布':
                winner='我'
                p_not_win += 1
                c_not_win = 0
            else:
                winner='你'
                c_not_win += 1
                p_not_win = 0

            if winner=='平局':
                char_print('   本轮为平局\033[0m\n')
            else :
                char_print(f'   本轮{winner}赢了👍\033[0m\n')
            if c_not_win == 3:
                char_print("嘤嘤嘤😥，连输了三把，不玩了(╯°□°)╯︵ ┻━┻！\n")
                break
            if p_not_win == 3:
                char_print("Sorry，连赢了你3把，请不要生气哦😏\n")
                break
            char_print("   还玩吗？")
            a = input("")

            if "不" in a:
                print("ok！如你所愿😀")
                break

def play_guess_n():
    remaining_chances = 5
    g_number = random.randint(50,200)
    s_number = g_number - random.randint(3,5)
    b_number = g_number + random.randint(3,5)
    think_over()
    char_print("\033[34m🤖:好的，猜数字游戏开始(五次机会,整数,直接写数字)\n")
    time.sleep(0.5)
    char_print(f"\033[34m   我想到了一个数字，它在\033[33m{s_number}\033[34m和\033[33m{b_number}\033[34m之间，你来猜吧:\033[0m")
    while True:
        a = input("")
        remaining_chances -= 1
        if remaining_chances == 0:
            char_print(f"\033[34m   机会用完了，正确答案是\033[33m{g_number}\033[34m，游戏结束!\033[0m\n")
            return None
        if a.isdigit():
            a = int(a)
            if a == g_number:
                char_print(f"\033[34m   猜对了，答案就是\033[33m{g_number}\033[34m!\033[0m\n")
                return None
            else:
                char_print(f"\033[34m   不对哦，还有\033[33m{remaining_chances}\033[34m次机会。再猜:\033[0m")

def play_math_challenge():
    think_over()
    right_number = 0
    time_list = []
    a_list = []
    char_print("\033[34m🤖:速算挑战开始！十秒内答题！\n   tip:除了数字别写别的，不会就敲n\n")
    s = ["+","-","*","/"]
    while True:
        t = f"{random.randint(2,20)}{random.choice(s)}{random.randint(2,20)}"
        t_a = eval(t)
        if "-" in str(t_a) or "." in str(t_a):
            while  "-" in str(t_a) or "." in str(t_a):
                t = f"{random.randint(2,20)}{random.choice(s)}{random.randint(2,20)}"
                t_a = eval(t)
        char_print(f"   算式'{t}=?'的结果：")
        start = time.time()
        a = input("")
        a_list.append(a)
        if not a == "n":
            try:
                a = int(a)
            except:
                char_print("   嗯?有违规字符，你犯规了😡！\n\033[0m")
                return None
        end = time.time()
        spend_time = int(end - start)
        time_list.append(spend_time)
        if len(time_list) > 0:
            for i in time_list:
                min_time = 20
                if i < min_time:
                    min_time = i
        if spend_time > 10:
            char_print(f"   哦哦，你用了{spend_time}秒，超时啦！\n   游戏结束😏\033[32m\n\n")
            char_print(f"   {'='*15}结算{'='*15}\n")
            char_print(f"   这场挑战，你答对了{right_number}道题。\n")
            char_print(f"   你最快的一次，只用了{min_time}秒就算出了结果。\n")
            char_print(f"   恭喜你！勇士！\033[0m")
            return None
        if a == "n":
            for i in a_list:
                if i == "n":
                    only_n = True
                else:
                    only_n = False
                    break
            if only_n:
                char_print("   好吧😀，这题你不会，进入结算：\033[32m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                char_print(f"   这场挑战，你答对了{right_number}道题。\n")
                char_print(f"   你最快的一次，只用了0秒就算出了结果。\n")
                char_print(f"   恭喜你！勇士！\033[0m\n")
                return None
            else:
                char_print("   好吧😀，这题你不会，进入结算：\033[32m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                char_print(f"   这场挑战，你答对了{right_number}道题。\n")
                char_print(f"   你最快的一次，只用了{spend_time}秒就算出了结果。\n")
                char_print(f"   恭喜你！勇士！\033[0m\n")
                return None
        elif a == eval(t):
            right_number += 1
            char_print("   答对啦！下一题👍\n")
        else:
            char_print("   不好！你答错啦！游戏结束👋\033[32m\n\n")
            char_print(f"   {'='*15}结算{'='*15}\n")
            char_print(f"   这场挑战，你答对了{right_number}道题。\n")
            char_print(f"   你最快的一次，只用了{min_time}秒就算出了结果。\n")
            char_print(f"   恭喜你！勇士！\n\033[0m")
            return None

#AI发疯函数
def become_crazy():
    global is_crazy
    global crazy_n
    if crazy_n > 19 or random.randint(1,100) < 11:
        is_crazy = False
        return None
    if is_crazy == True:
        crazy_n += 1
        return random.choice(CRAZY_A[random.randint(1,6)])
    if random.randint(1,100) < 6:
        is_crazy = True
        crazy_n += 1
        return random.choice(CRAZY_A[random.randint(1,6)])
    return None

#主程序函数
def run_app():
    print("\033[33m正在启动ShallowSeek,请稍等...\033[0m",end = '\r')
    time.sleep(1)
    print("\033[32mShallowSeek已启动!           \033[0m")
    time.sleep(0.5)
    char_print("\n\033[34m嗨!我是ShallowSeek(浅度求索),有什么可以帮你的吗?\033[0m")
    char_print("\n\033[34mn退出,h帮助,v看版本\033[0m\n")
    while True:
        t = input('说点什么：')
        clear_input_lines(t, '说点什么：')
        print(f"🧔:{t}")
        if t == "e":
            char_print("\033[32m🤖:再见啦,下次再聊哦!\033[0m")
            time.sleep(3)
            break
        if t == "h":
            char_print("\033[34m🤖:支持一些问题,比如:\n\033[0m")
            char_print("\033[34m   你是谁、天气怎么样、你会做什么、你好\n   目前只会算阿拉伯数字算式,小数固定保留10位小数\n   内置石头剪刀布游戏\n\033[0m")
            continue
        if t == "v":
            char_print(f"\033[34m🤖:版本号-{v}\n\033[0m")
            continue
        if t == "yxh4321":
            p.pprint(Q_A)
            continue
        if t == "h_X_y":
            p.pprint(BUSY_A)
            continue
        a = answer(t)
        if a == None:
            continue
        if len(a) > 100:
            a = f"{a:.100}......"
        last_say.clear()
        last_say.append(t)
        last_say.append(a)
        think_over()
        if is_crazy:
            char_print(f"\033[36m🤖:{a}\033[0m\n")
        elif a in ERROR_A:
            char_print(f"\033[31m🤖:{a}\033[0m\n")
        else:
            char_print(f"\033[34m🤖:{a}\033[0m\n")

#主程序
if __name__ == "__main__":
    run_app()