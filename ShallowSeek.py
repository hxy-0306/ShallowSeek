#导入模块
import re
import os
import ast
import sys
import time
import json
import shutil
import random
import subprocess
import builtins
from Q_A import * 
import unicodedata
import pprint as p
from PIL import Image, ImageDraw, ImageFont
#定义变量
crazy_n = 0
is_crazy = False
v = 1.7
last_say = []
say_list = []
allowed = (ast.Expression, #表示算式
            ast.BinOp, #二元运算
            ast.UnaryOp, #一元运算
            ast.Constant, #数字
            ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow, #四则运算+次方
            ast.USub #负号
            )
happy = 50
satiety = 50
clean = 50

#终端原始流捕获（只在小游戏/宠物期间开启）
_cap = None

class _Tee:
    '''把写往 stdout 的内容同时抄一份给捕获器'''
    def __init__(self, target):
        self._t = target
    def write(self, s):
        self._t.write(s)
        if _cap is not None:
            _cap.append(s)
        return len(s)
    def flush(self):
        self._t.flush()
    def __getattr__(self, name):
        return getattr(self._t, name)

sys.stdout = _Tee(sys.stdout)

_orig_input = builtins.input
def _rec_input(prompt=""):
    '''记录用户输入回显（终端回显不经 sys.stdout，需要手工补）'''

    s = _orig_input(prompt)
    if _cap is not None:
        if prompt:
            _cap.append(prompt)
        _cap.append(f"{s}\n")
    return s
builtins.input = _rec_input

def begin_capture():
    '''开始捕获一个游戏片段'''
    global _cap
    _cap = []

def end_capture():
    '''结束捕获并返回原始字节流'''
    global _cap
    raw = "".join(_cap) if _cap else ""
    _cap = None
    return raw

#定义函数
def init():
    global crazy_n,is_crazy,last_say,say_list,happy,satiety,clean
    crazy_n = 0
    is_crazy = False
    last_say = []
    say_list = []
    happy = 50
    satiety = 50
    clean = 50

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

def note(user_text,ai_text):
    '''只更新 last_say，不入 say_list'''
    text = re.sub(r"\033\[[0-?]*[ -/]*[@-~]", "", str(ai_text)).strip()
    if not text:
        return
    last_say.clear()
    last_say.append(user_text)
    last_say.append(text)

def record_game(trigger,summary,raw):
    '''游戏片段：只追加一条带原始流的记录，不改 last_say'''
    say_list.append([trigger,summary,None,raw])

def record_raw(text):
    '''原样记录一行输出（无 🧔/🤖 前缀，保留颜色码）'''
    say_list.append([None,text,"raw"])

def record(user_text,ai_text,color=None,touch_last=True):
    '''记录一轮对话：并入 say_list，默认同时更新 last_say；
       捕获游戏期间自动降级为 note，避免逐轮入档。
       color 传输出时的颜色码（94蓝/96紫/91红），回放时还原颜色'''
    text = re.sub(r"\033\[[0-?]*[ -/]*[@-~]", "", str(ai_text)).strip()
    if not text:
        return
    if _cap is not None:
        note(user_text,text)
    else:
        if touch_last:
            note(user_text,text)
        if color:
            say_list.append([user_text,text,color])
        else:
            say_list.append([user_text,text])

def display_width(text):
    '''估算字符串在终端中占用的列数'''
    width = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def clean_float_result(result):
    '''保留10位小数，解决一定的计算错误'''
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return (f"{result:.10f}").rstrip('0').rstrip('.')

def pysum(s):
    '''用eval计算算式的结果并返回，建议加上限制/检测'''
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
    '''清除提示语和用户输入'''
    columns = shutil.get_terminal_size((80, 20)).columns
    total_width = display_width(prompt) + display_width(text)
    lines = max(1, (total_width + columns - 1) // columns)
    for _ in range(lines):
        print("\033[F\033[2K", end='')

def clear_display_lines(lines):
    '''清除一组文字'''
    columns = shutil.get_terminal_size((80, 20)).columns
    row_count = 0
    for line in lines:
        visible_line = re.sub(r"\033\[[0-?]*[ -/]*[@-~]", "", line)
        width = display_width(visible_line)
        row_count += max(1, (width + columns - 1) // columns)
    for _ in range(row_count):
        print("\033[F\033[2K", end="", flush=True)

def think_over():
    '''模拟思考过程'''
    print("\033[94m正在思考",end="",flush=True)
    for _ in range(5):
        print(".",end="",flush=True)
        time.sleep(0.4)
    print('\r               ', end = '\r')

def answer(question):
    '''shallowseek的主要回答函数'''
    global is_crazy
    if "速算" in question or "挑战" in question or "数学" in question:
        begin_capture()
        try:
            play_math_challenge(question)
        finally:
            record_game(question,"（速算挑战）",end_capture())
        return None
    if "石头剪刀布" in question or "猜拳" in question:
        begin_capture()
        try:
            play_rqs(question)
        finally:
            record_game(question,"（石头剪刀布）",end_capture())
        return None
    if "猜数字" in question:
        begin_capture()
        try:
            play_guess_n(question)
        finally:
            record_game(question,"（猜数字）",end_capture())
        return None
    if "游戏" in question:
        begin_capture()
        try:
            if random.randint(0,1) == 0:
                play_rqs(question)
            else:
                play_guess_n(question)
        finally:
            record_game(question,"（小游戏）",end_capture())
        return None
    if "发疯" in question or "疯狂" in question:
        think_over()
        if not is_crazy:
            is_crazy = True
            return "如你所愿！我要疯了……哇哩哇哩哇！你好！我是疯狂戴夫！"
        return "你说什么?告诉你，我已经疯狂了👾!"
    if "恢复" in question:
        think_over()
        if is_crazy:
            is_crazy = False
            return "好!这就恢复正常👋"
        return "你在说啥?我很正常啊🤔"
    if "生成" in question and ("图片" in question or "照片" in question):
        think_over()
        return make_png()
    if "宠物" in question:
        think_over()
        begin_capture()
        try:
            virtual_pet(question)
        finally:
            record_game(question,"（电子宠物）",end_capture())
        return None
    if "存档" in question or "保存" in question:
        think_over()
        save()
        return None
    if "读档" in question or "加载" in question:
        think_over()
        load()
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
        if re.search(r"^\s*$",question):
            return random.choice(Q_A["not have"])
        for q in Q_A:
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
    '''生成图片函数'''
    print("\033[94m正在生成",end="",flush=True)
    for _ in range(5):
        print(".",end="",flush=True)
        time.sleep(0.4)
    print('\r               ', end = '\r')
    try:
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
        return f"已生成：图片.png，位置:{path}\\图片.png"
    except:
        return "图片生成失败❌"

def virtual_pet(trigger="宠物"):
    '''电子宠物函数'''
    global happy,satiety,clean
    pet_says = {"good":["好开心！😀","嗝！真满足，好喜欢主人！","我爱洗澡，鳞片好好👍"],"not bad":["心情不错！","五分饱！活到老！","一点水草，无伤大雅😊"],"bad":["不开心到吐泡🫧","好饿啊！快成鱼骨头了🦴！","一身水草，讨厌🌿！"]}
    display_lines = [
        f"{'='*5}电子宠物模式{'='*5}",
        f"快乐值:{happy}/100",
        f"饱食度:{satiety}/100",
        f"清洁度:{clean}/100",
        "🐟:你好呀！我叫小鱼！",
        "="*22,
        "(1玩耍,2喂食,3洗澡,exit退出):",
    ]
    char_print(f"\033[94m{'='*5}电子宠物模式{'='*5}\n")
    char_print(f"快乐值:{happy}/100\n")
    char_print(f"饱食度:{satiety}/100\n")
    char_print(f"清洁度:{clean}/100\n")
    char_print("\033[93m🐟:你好呀！我叫小鱼！\033[94m\n")
    char_print(f"{'='*22}\n")
    char_print("(1玩耍,2喂食,3洗澡,exit退出):\033[0m")
    record(trigger,f"进入电子宠物模式｜快乐{happy} 饱食{satiety} 清洁{clean}")
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
            bye = "🐟:Good——bye!!"
        elif happy < 30 and clean < 30 and satiety < 30:
            bye = "🐟:Bad——bye."
        else:
            bye = "🐟:Bye!"
        record(a,bye)
        char_print(f"\033[93m{bye}")
        print("\033[0m")
        return None
    happy -= random.randint(2,3)
    satiety -= random.randint(1,2)
    clean -= random.randint(1,2)
    happy = max(0,min(100,happy))
    satiety = max(0,min(100,satiety))
    clean = max(0,min(100,clean))
    while True:
        clear_display_lines(display_lines[:-1] + [display_lines[-1] + a])
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
        display_lines = [
            f"{'='*5}电子宠物模式{'='*5}",
            f"快乐值:{happy}/100",
            f"饱食度:{satiety}/100",
            f"清洁度:{clean}/100",
            f"🐟:{say}",
            "="*22,
            "(1玩耍,2喂食,3洗澡,exit退出):",
        ]
        print(f"\033[94m{'='*5}电子宠物模式{'='*5}")
        print(f"快乐值:{happy}/100")
        print(f"饱食度:{satiety}/100")
        print(f"清洁度:{clean}/100")
        print(f"\033[93m🐟:{say}\033[94m")
        print(f"{'='*22}")
        print("(1玩耍,2喂食,3洗澡,exit退出):\033[0m",end="",flush=True)
        record(a,f"🐟:{say}｜快乐{happy} 饱食{satiety} 清洁{clean}")
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
                bye = "🐟:Good——bye!!"
            elif happy < 30 and clean < 30 and satiety < 30:
                bye = "🐟:Bad——bye."
            else:
                bye = "🐟:Bye!"
            record(a,bye)
            char_print(f"\033[93m{bye}")
            print("\033[0m")
            return None
        happy -= random.randint(1,2)
        satiety -= random.randint(0,1)
        clean -= random.randint(0,1)
        happy = max(0,min(100,happy))
        satiety = max(0,min(100,satiety))
        clean = max(0,min(100,clean))

def can_ast(code):
    '''检测输入是否是一个算式'''
    try:
        tree = ast.parse(code,mode="eval")
    except:
        return False
    for node in ast.walk(tree):
        if not isinstance(node,allowed):
            return False
    return True

def save():
    char_print("\033[94m输入存档名称:")
    name = input("")
    global crazy_n,is_crazy,last_say,happy,satiety,clean,say_list
    data = {
        "crazy_n":crazy_n,
        "is_crazy":is_crazy,
        "last_say":last_say,
        "happy":happy,
        "satiety":satiety,
        "clean":clean,
        "say_list":say_list
    }
    try:
        with open(f"{name}.json","w",encoding="utf-8") as file:
            json.dump(data,file,ensure_ascii=False, indent=2)
        char_print("\033[94m已存档!\033[0m\n")
    except:
        char_print("\033[94m存档失败!\033[0m\n")

def load():
    global crazy_n,is_crazy,last_say,happy,satiety,clean,say_list
    char_print("\033[94m输入存档名称:")
    name = input("")
    if os.path.exists(f"{name}.json"):
        with open(f"{name}.json","r",encoding="utf-8") as file:
            data = json.load(file)
            crazy_n = data.get("crazy_n",crazy_n)
            is_crazy = data.get("is_crazy",is_crazy)
            last_say = data.get("last_say",last_say)
            happy = data.get("happy",happy)
            satiety = data.get("satiety",satiety)
            clean = data.get("clean",clean)
            say_list = data.get("say_list",say_list)
        clear = "cls" if os.name == "nt" else "clear"
        subprocess.run(clear,shell=True)
        char_print("\033[93m正在同步...\033[0m\n")
        for i in say_list:
            third = i[2] if len(i) > 2 else None
            if len(i) > 3 and i[3]:
                sys.stdout.write(i[3])
                sys.stdout.flush()
            elif third == "raw":
                sys.stdout.write(i[1])
            elif third and chr(27) in third:
                sys.stdout.write(third)
                sys.stdout.flush()
            elif third:
                if i[0]:
                    print(f"🧔:{i[0]}")
                print(f"\033[{third}m🤖:{i[1]}\033[0m")
            else:
                if i[0]:
                    print(f"🧔:{i[0]}")
                print(f"\033[94m🤖:{i[1]}\033[0m")

    else:
        char_print("\033[94m存档不存在❌\033[0m\n")
        record("读档","存档不存在❌")
#游戏函数
def play_rqs(trigger="石头剪刀布"):
    '''石头剪刀布游戏'''
    c_not_win = 0
    p_not_win = 0
    think_over()
    char_print("\033[94m🤖:好嘞，石头剪刀布游戏开始!\n")
    record(trigger,"好嘞，石头剪刀布游戏开始!")
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
            record(user_choice,f'你出{user_choice}，我出{computer_choice}，本轮为平局')
            char_print('   本轮为平局\033[0m\n')
        else :
            record(user_choice,f'你出{user_choice}，我出{computer_choice}，本轮{winner}赢了')
            char_print(f'   本轮{winner}赢了👍\033[0m\n')
        if c_not_win == 3:
            char_print("嘤嘤嘤😥，连输了三把，不玩了(╯°□°)╯︵ ┻━┻！\n")
            record("石头剪刀布","嘤嘤嘤😥，连输了三把，不玩了(╯°□°)╯︵ ┻━┻！")
            break
        if p_not_win == 3:
            char_print("Sorry，连赢了你3把，请不要生气哦😏\n")
            record("石头剪刀布","Sorry，连赢了你3把，请不要生气哦😏")
            break
        char_print("   还玩吗？")
        a = input("")

        if "不" in a:
            record(a,"ok！如你所愿😀")
            print("ok！如你所愿😀")
            break

def play_guess_n(trigger="猜数字"):
    '''猜数字游戏'''
    remaining_chances = 5
    g_number = random.randint(50,200)
    s_number = g_number - random.randint(3,5)
    b_number = g_number + random.randint(3,5)
    think_over()
    char_print("\033[94m🤖:好的，猜数字游戏开始(五次机会,整数,直接写数字)\n")
    record(trigger,f"好的，猜数字游戏开始(五次机会,整数,直接写数字)，数字在{s_number}和{b_number}之间")
    time.sleep(0.5)
    char_print(f"\033[94m   我想到了一个数字，它在\033[93m{s_number}\033[94m和\033[93m{b_number}\033[94m之间，你来猜吧:\033[0m")
    while True:
        a = input("")
        guess = a
        remaining_chances -= 1
        if a.isdigit():
            a = int(a)
            if a == g_number:
                record(guess,f"猜对了，答案就是{g_number}!")
                char_print(f"\033[94m   猜对了，答案就是\033[93m{g_number}\033[94m!\033[0m\n")
                return None
            else:
                if remaining_chances != 0:
                    record(guess,f"不对哦，还有{remaining_chances}次机会")
                    char_print(f"\033[94m   不对哦，还有\033[93m{remaining_chances}\033[94m次机会。再猜:\033[0m")
        else:
            if not remaining_chances == 0:
                record(guess,f"不对哦，还有{remaining_chances}次机会")
                char_print(f"\033[94m   不对哦，还有\033[93m{remaining_chances}\033[94m次机会。再猜:\033[0m")
        if remaining_chances == 0:
            record(guess,f"机会用完了，正确答案是{g_number}，游戏结束!")
            char_print(f"\033[94m   机会用完了，正确答案是\033[93m{g_number}\033[94m，游戏结束!\033[0m\n")
            return None

def play_math_challenge(trigger="速算挑战"):
    '''速算挑战游戏'''
    right_number = 0
    small_time = 5
    def summary():
        '''拼结算文案，按最新的答对题数'''
        if right_number > 0:
            return (f"这场挑战，你答对了{right_number}道题。"
                    f"你最快的一次，只用了{small_time}秒就算出了结果。恭喜你！勇士！")
        return "这场挑战，你没有答题。继续努力！勇士！"
    char_print("\033[94m🤖:速算挑战开始！五秒内答题！\n   tip:除了数字别写别的，不会就敲n\n")
    record(trigger,"速算挑战开始！五秒内答题！")
    s = "+-*/"
    while True:
        #生成算式
        t = f"{random.randint(2,20)}{random.choice(s)}{random.randint(2,20)}"
        right_answer = eval(t)
        c = eval(t)
        d = int(eval(t))
        if c == d:
            right_answer = int(right_answer)
        if "-" in str(right_answer) or "." in str(right_answer):
            while  "-" in str(right_answer) or "." in str(right_answer):
                t = f"{random.randint(2,20)}{random.choice(s)}{random.randint(2,20)}"
                right_answer = eval(t)
        #出题
        char_print(f"   算式'{t}=?'的结果:\033[0m")
        print("\033[94m",end="",flush=True)
        start = time.time()
        a = input("")
        if not a == "n":
            do_it = True
            try:
                a = int(a)
            except:
                record(f"{t}=?", "违规字符，犯规")
                char_print("   嗯?有违规字符，你犯规了😡！\n\033[0m")
                return None
            end = time.time()
            this_time = int(end - start)
            if this_time > 5:
                is_timeout = True
            else:
                is_timeout = False

            if this_time < small_time:
                small_time = this_time

            if a == right_answer:
                is_right = True
            else:
                is_right = False

            

        else:
            do_it = False
        #判断和结算
        #做没做
        if do_it:
            #超不超时
            if is_timeout:
                record(f"{t}=?", f"用了{this_time}秒，超时；正确答案是{right_answer}")
                char_print(f"   哦哦，你用了{this_time}秒，超时!😏\033[92m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                say = summary()
                char_print(f"   {say}\n\033[0m")
                record(trigger,say)
                return None
            #对不对
            if is_right:
                right_number += 1
                record(f"{t}=?", f"答对啦，用时{this_time}秒")
                char_print("   答对啦！下一题👍\n")
            else:
                record(f"{t}=?", f"答错啦；正确答案是{right_answer}")
                char_print("   不好！你答错啦！游戏结束👋\033[92m\n\n")
                char_print(f"   {'='*15}结算{'='*15}\n")
                say = summary()
                char_print(f"   {say}\n\033[0m")
                record(trigger,say)
                return None
        else:
            record(f"{t}=?", f"不会，跳过；正确答案是{right_answer}")
            char_print("   好吧😀，这题你不会，进入结算：\033[92m\n\n")
            char_print(f"   {'='*15}结算{'='*15}\n")
            say = summary()
            char_print(f"   {say}\n\033[0m")
            record(trigger,say)
            return None

#AI发疯函数
def become_crazy():
    '''模拟AI的“发疯”行为'''
    global is_crazy
    global crazy_n
    if crazy_n > 9 or random.randint(1,100) < 11:
        is_crazy = False
        crazy_n = 0
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
    '''shallowseek的主程序'''
    print("\033[93m正在启动ShallowSeek,请稍等...\033[0m",end = '\r')
    time.sleep(1)
    print("\033[92mShallowSeek已启动!           \033[0m")
    time.sleep(0.5)
    char_print("\n\033[94m嗨!我是ShallowSeek(浅度求索),有什么可以帮你的吗?\033[0m")
    char_print("\n\033[94mh帮助,v看版本,n开启新对话(偷偷告诉你，计算要谨慎)\033[0m\n")
    record_raw("\n\033[94m嗨!我是ShallowSeek(浅度求索),有什么可以帮你的吗?\033[0m")
    record_raw("\n\033[94mh帮助,v看版本,n开启新对话(偷偷告诉你，计算要谨慎)\033[0m\n")
    while True:
        t = input('说点什么：')
        clear_input_lines(t, '说点什么：')
        print(f"🧔:{t}")
        if t == "h":
            char_print("\033[94m🤖:支持一些问题,比如:\n\033[0m")
            char_print("\033[94m   你是谁、天气怎么样、你会做什么、你好\n   支持算数字算式,小数保留10位(有风险，不要算太大的冥)\n   内置小游戏\n\033[0m")
            record(t,"支持一些问题,比如:你是谁、天气怎么样、你会做什么、你好；支持算数字算式,小数保留10位(有风险，不要算太大的冥)；内置小游戏","94")
            continue
        if t == "v":
            char_print(f"\033[94m🤖:版本号-{v}\n\033[0m")
            record(t,f"版本号-{v}","94")
            continue
        if t == "n":
            clear = "cls" if os.name == "nt" else "clear"
            subprocess.run(clear,shell=True)
            init()
            char_print("\033[94m已开启新对话!\033[0m\n")
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
        if is_crazy:
            color = "96"
        elif a in ERROR_A:
            color = "91"
        else:
            color = "94"
        record(t,a,color)
        think_over()
        char_print(f"\033[{color}m🤖:{a}\033[0m\n")

#主程序
if __name__ == "__main__":
    run()