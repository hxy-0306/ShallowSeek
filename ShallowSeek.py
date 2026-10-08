#导入模块
import re
import os
import ast
import sys
import time
import shutil
import random
from Q_A import * 
import unicodedata
import pprint as p
from PIL import Image, ImageDraw, ImageFont
#定义变量
crazy_n = 0
is_crazy = False
v = 1.4
last_say = []
allowed = (ast.Expression, #表示算式
           ast.BinOp, #二元运算
           ast.UnaryOp, #一元运算
           ast.Constant, #数字
           ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow, #四则运算+次方
           ast.USub #负号
           )
#电子宠物变量
happy = 50
satiety = 50
clean = 50

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
    if len(s) < 30:
        try:
            num = eval(s)
            num = clean_float_result(num)
            return f"答案是：{num}"
        except:
            return "不知道是谁的问题，反正我没算出来😏"
    else:
        return "算式太长了,俺拒绝计算🤪!"

def clear_input_lines(text, prompt):
    columns = shutil.get_terminal_size((80, 20)).columns
    total_width = display_width(prompt) + display_width(text)
    lines = max(1, (total_width + columns - 1) // columns)
    for _ in range(lines):
        print("\033[F\033[2K", end='')

def think_over():
    print("\033[94m正在思考",end="",flush=True)
    for _ in range(5):
        print(".",end="",flush=True)
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
            char_print("\033[96m🤖:如你所愿！我要疯了……哇哩哇哩哇！你好！我是疯狂戴夫！\033[0m\n")
        else:
            char_print("\033[96m🤖:你说什么?告诉你，我已经疯狂了👾!\033[0m\n")
        return None
    if "恢复" in question:
        think_over()
        if is_crazy:
            is_crazy = False
            char_print("\033[94m🤖:好!这就恢复正常👋\033[0m\n")
        else:
            char_print("\033[94m🤖:你在说啥?我很正常啊🤔\033[0m\n")
        return None
    if "生成" in question and ("图片" in question or "照片" in question):
        think_over()
        make_png()
        return None
    if "宠物" in question:
        think_over()
        virtual_pet()
        return None
    c = become_crazy()
    if c == None:
        try:
            question = question.replace("=","").replace("?","").replace("!","").replace(" ","").replace("？","").replace("！","")
        except:
            pass
        if "刚刚" in question or "之前" in question or "刚才" in question:
            if not last_say == []:
                return f"刚才你问：“{last_say[0]}”，我回答：“{last_say[1]}”"
            else:
                return "我们还什么都没聊呢🧐"
        if can_ast(question):
            return pysum(question)
        for q in Q_A:
            if re.search(r"^\s*$",question):
                return random.choice(Q_A["not have"])
            if isinstance(Q_A[q],dict):
                if q in question:
                    for t in Q_A[q]:
                        if t in question:
                            return(random.choice(Q_A[q][t]))
            elif q in question:
                return(random.choice(Q_A[q]))
        return random.choice(BUSY_A)
    else:
        return c

def make_png():
    print("\033[94m正在生成",end="",flush=True)
    for _ in range(5):
        print(".",end="",flush=True)
        time.sleep(0.4)
    print('\r               ', end = '\r')

    path = os.getcwd()
    img = Image.new('RGB', (400, 355), 'black')
    draw = ImageDraw.Draw(img)

    text = """    哈哈哈！开个玩笑！
    这张图片没有任何内容！""" 
    try:
        font_path = os.path.join(sys._MEIPASS,"font.ttf")
    except:
        font_path = "font.ttf"
    font = ImageFont.truetype(font_path,20)

    bbox = draw.textbbox((0, 0), text, font=font)
    x = (400 - (bbox[2] - bbox[0])) // 2
    y = (355 - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), text, fill='white', font=font)

    img.save('图片.png')
    char_print(f"\033[94m🤖:已生成：图片.png，位置:{path}\\图片.png\n\033[0m")

def virtual_pet():
    global happy,satiety,clean
    pet_says = {"good":["好开心！😀","嗝！真满足，好喜欢主人！","我爱洗澡，鳞片好好👍"],"not bad":["心情不错！","五分饱！活到老！","一点水草，无伤大雅😊"],"bad":["不开心到吐泡🫧","好饿啊！快成鱼骨头了🦴！","一身水草，讨厌🌿！"]}
    char_print(f"\033[94m{'='*5}电子宠物模式{'='*5}\n")
    char_print(f"快乐值:{happy}/100\n")
    char_print(f"饱食度:{satiety}/100\n")
    char_print(f"清洁度:{clean}/100\n")
    char_print("\033[93m🐟:你好呀！我叫小鱼！\033[94m\n")
    char_print(f"{'='*22}\n")
    char_print("(1玩耍,2喂食,3洗澡,exit退出):\033[0m")
    a = input("")
    if a == "1":
        happy += max(3,clean // 10)
        clean -= random.randint(3,5)
        satiety -= random.randint(2,5)
    elif a == "2":
        satiety += random.randint(8,12)
        clean -= random.randint(2,4)
    elif a == "3":
        clean += random.randint(8,12)
        satiety -= random.randint(1,3)
    elif a == "exit":
        if happy > 49 and clean > 49 and satiety > 49:
            char_print("\033[93m🐟:Good——bye!!")
        elif happy < 30 and clean < 30 and satiety < 30:
            char_print("\033[93m🐟:Bad——bye.")
        else:
            char_print("\033[93m🐟:Bye!")
        print("\033[0m")
        return None
    happy -= random.randint(2,3)
    satiety -= random.randint(1,2)
    clean -= random.randint(1,2)
    happy = max(0,min(100,happy))
    satiety = max(0,min(100,satiety))
    clean = max(0,min(100,clean))
    while True:
        for _ in range(7):
            print("\033[F\033[2K",end="",flush=True)
        num = random.randint(1,3)
        if num == 1:
            if happy >= 70:
                say = pet_says["good"][0]
            elif happy >= 40:
                say = pet_says["not bad"][0]
            else:
                say = pet_says["bad"][0]
        elif num == 2:
            if satiety >= 70:
                say = pet_says["good"][1]
            elif satiety >= 40:
                say = pet_says["not bad"][1]
            else:
                say = pet_says["bad"][1]
        else:
            if clean >= 70:
                say = pet_says["good"][2]
            elif clean >= 40:
                say = pet_says["not bad"][2]
            else:
                say = pet_says["bad"][2]
        print(f"\033[94m{'='*5}电子宠物模式{'='*5}")
        print(f"快乐值:{happy}/100")
        print(f"饱食度:{satiety}/100")
        print(f"清洁度:{clean}/100")
        print(f"\033[93m🐟:{say}\033[94m")
        print(f"{'='*22}")
        print("(1玩耍,2喂食,3洗澡,exit退出):\033[0m",end="",flush=True)
        a = input("")
        if a == "1":
            happy += max(3,clean // 10)
            clean -= random.randint(3,5)
            satiety -= random.randint(2,5)
        elif a == "2":
            satiety += random.randint(8,12)
            clean -= random.randint(2,4)
        elif a == "3":
            clean += random.randint(8,12)
            satiety -= random.randint(1,3)
        elif a == "exit":
            if happy > 49 and clean > 49 and satiety > 49:
                char_print("\033[93m🐟:Good——bye!!")
            elif happy < 30 and clean < 30 and satiety < 30:
                char_print("\033[93m🐟:Bad——bye.")
            else:
                char_print("\033[93m🐟:Bye!")
            print("\033[0m")
            return None
        happy -= random.randint(1,2)
        satiety -= random.randint(0,1)
        clean -= random.randint(0,1)
        happy = max(0,min(100,happy))
        satiety = max(0,min(100,satiety))
        clean = max(0,min(100,clean))

def can_ast(code):
    try:
        tree = ast.parse(code,mode="eval")
    except:
        return False
    for node in ast.walk(tree):
        if not isinstance(node,allowed):
            return False
    return True

#游戏函数
def play_rqs():
        c_not_win = 0
        p_not_win = 0
        think_over()
        char_print("\033[94m🤖:好嘞，石头剪刀布游戏开始!\n")
        while True:
            random_choice=random.randint(0,2)

            if random_choice==0:
                computer_choice='石头'
            elif random_choice==1:
                computer_choice='剪刀'
            else:
                computer_choice='布'

            char_print('\033[94m   你出石头、剪刀还是布？')
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
    char_print("\033[94m🤖:好的，猜数字游戏开始(五次机会,整数,直接写数字)\n")
    time.sleep(0.5)
    char_print(f"\033[94m   我想到了一个数字，它在\033[93m{s_number}\033[94m和\033[93m{b_number}\033[94m之间，你来猜吧:\033[0m")
    while True:
        a = input("")
        remaining_chances -= 1
        if a.isdigit():
            a = int(a)
            if a == g_number:
                char_print(f"\033[94m   猜对了，答案就是\033[93m{g_number}\033[94m!\033[0m\n")
                return None
            else:
                char_print(f"\033[94m   不对哦，还有\033[93m{remaining_chances}\033[94m次机会。再猜:\033[0m")
        if remaining_chances == 0:
            char_print(f"\033[94m   机会用完了，正确答案是\033[93m{g_number}\033[94m，游戏结束!\033[0m\n")
            return None

def play_math_challenge():
    think_over()
    right_number = 0
    time_list = []
    a_list = []
    char_print("\033[94m🤖:速算挑战开始！五秒内答题！\n   tip:除了数字别写别的，不会就敲n\n")
    s = "+-*/"
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
        if spend_time > 5:
            char_print(f"   哦哦，你用了{spend_time}秒，超时啦！\n   游戏结束😏\033[92m\n\n")
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
                char_print("   好吧😀，这题你不会，进入结算：\033[92m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                char_print(f"   这场挑战，你没有答题。\n")
                char_print(f"   继续努力！勇士！\033[0m\n")
                return None
            else:
                char_print("   好吧😀，这题你不会，进入结算：\033[92m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                char_print(f"   这场挑战，你答对了{right_number}道题。\n")
                char_print(f"   你最快的一次，只用了{spend_time}秒就算出了结果。\n")
                char_print(f"   恭喜你！勇士！\033[0m\n")
                return None
        elif a == eval(t):
            right_number += 1
            char_print("   答对啦！下一题👍\n")
        else:
            char_print("   不好！你答错啦！游戏结束👋\033[92m\n\n")
            char_print(f"   {'='*15}结算{'='*15}\n")
            char_print(f"   这场挑战，你答对了{right_number}道题。\n")
            char_print(f"   你最快的一次，只用了{min_time}秒就算出了结果。\n")
            char_print(f"   恭喜你！勇士！\n\033[0m")
            return None

#AI发疯函数
def become_crazy():
    global is_crazy
    global crazy_n
    if crazy_n > 9 or random.randint(1,100) < 11:
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
def run():
    print("\033[93m正在启动ShallowSeek,请稍等...\033[0m",end = '\r')
    time.sleep(1)
    print("\033[92mShallowSeek已启动!           \033[0m")
    time.sleep(0.5)
    char_print("\n\033[94m嗨!我是ShallowSeek(浅度求索),有什么可以帮你的吗?\033[0m")
    char_print("\n\033[94mh帮助,v看版本(偷偷告诉你，计算要谨慎)\033[0m\n")
    while True:
        t = input('说点什么：')
        clear_input_lines(t, '说点什么：')
        print(f"🧔:{t}")
        if t == "h":
            char_print("\033[94m🤖:支持一些问题,比如:\n\033[0m")
            char_print("\033[94m   你是谁、天气怎么样、你会做什么、你好\n   支持算数字算式,小数保留10位(有风险，不要算太大的冥)\n   内置小游戏\n\033[0m")
            continue
        if t == "v":
            char_print(f"\033[94m🤖:版本号-{v}\n\033[0m")
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
        if len(a) > 300:
            a = f"{a:.300}......"
        last_say.clear()
        last_say.append(t)
        last_say.append(a)
        think_over()
        if is_crazy:
            char_print(f"\033[96m🤖:{a}\033[0m\n")
        elif a in ERROR_A:
            char_print(f"\033[91m🤖:{a}\033[0m\n")
        else:
            char_print(f"\033[94m🤖:{a}\033[0m\n")

#主程序
if __name__ == "__main__":
    run()