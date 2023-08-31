from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ParseMode, \
    BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, \
    ChatMemberHandler
import telegram, base64, os, time
from tools import get_session, Record, Recharge, register, User, Session, test_str, find_str, get_code, Holding, \
    distribute_red_packet, Snatch, Return_log, Reward_log, shunzi3, shunzi4, is_baozi3, is_baozi4, Conf, Withdrawal, \
    Chou_li
from datetime import datetime, date
import random, threading, json
from sqlalchemy import func, Date



def qidong():
    global global_data
    # 读取数据库配置信息
    session = Session()
    session.expire_all()
    try:
        objs = session.query(Conf).all()
    except Exception as e:
        print(e)
        session.close()
        return
    for obj in objs:
        if obj.typestr == "float":
            value = float(obj.value)
        elif obj.typestr == "list":
            value = json.loads(obj.value)
        elif obj.typestr == "int":
            value = int(obj.value)
        elif obj.typestr == "str":
            value = str(obj.value)
        else:
            value = obj.value
        global_data[obj.name] = value


qidong()

commands = [
    BotCommand(command="start", description="开始使用机器人"),
    BotCommand(command="invite", description="创建邀请链接"),
    BotCommand(command="help", description="帮助信息"),
    BotCommand(command="recharge", description="自动充值"),
    BotCommand(command="wanfa", description="玩法"),
]
TOKEN = global_data.get("TOKEN")
updater = Updater(token=TOKEN, use_context=True, request_kwargs=proxy_config)
updater.bot.set_my_commands(commands)
dispatcher = updater.dispatcher


def get_num():
    a = random.randint(1, 999)
    # 将整数转换为三位数的字符串
    a_str = str(a).zfill(3)
    return a_str


def turn_off(update, context):
    context.bot.delete_message(update.effective_chat.id, message_id=update.callback_query.message.message_id)
    context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='已关闭！')


# 取消订单
def move_order(update, context):
    print("开始取消订单")
    session = get_session()
    info = update.callback_query.to_dict()
    # tg的id
    t_id = info["from"]["id"]
    try:
        order = session.query(Recharge).filter_by(t_id=t_id, status=2).first()
    except Exception as e:
        print("查询订单出错")
        context.bot.send_message(update.effective_chat.id, "取消订单失败，请联系客服：@toumingde")
        session.close()
        return
    if not order:
        print("订单不存在")
        context.bot.send_message(update.effective_chat.id, "取消订单失败，请联系客服：@toumingde")
        session.close()
        return
    order.status = 4
    try:
        session.add(order)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        context.bot.send_message(update.effective_chat.id, "取消订单失败，请联系客服：@toumingde")
        return
    order_id = order.id
    firstname = order.firstname
    create_time = order.create_time
    money = order.money
    content = """
              <b>亲爱的客户：%s，您的订单id为：%s已被取消</b>
            
            ➖➖➖➖➖➖➖➖➖➖
            订单创建时间：%s
            转账金额: %s USDT
            ➖➖➖➖➖➖➖➖➖➖

    """ % (firstname, order_id, create_time, money)
    button_list = []
    for each in ['关闭', "再次充值"]:
        button_list.append(InlineKeyboardButton(each, callback_data=each))
    inline_button = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    context.bot.send_message(update.effective_chat.id, content, parse_mode=ParseMode.HTML, reply_markup=inline_button)
    dispatcher.add_handler(CallbackQueryHandler(turn_off, pattern='^关闭$'))
    dispatcher.add_handler(CallbackQueryHandler(recharge, pattern='^再次充值$'))




def create_order(update, context):
    session = get_session()
    Admin_name = global_data.get("Admin_name", "toumingde")
    # 我的钱包地址
    myaddress = global_data.get("My_address", "TAZ5gPwfU4bn14dKRqJXbCZJGJMqgoJsaf")
    info = update.callback_query.to_dict()
    # tg的id
    t_id = info["from"]["id"]
    # 1.检测是否存在待支付的订单
    try:
        order = session.query(Recharge).filter_by(status=2, t_id=t_id).first()
    except Exception as e:
        print(e)
        context.bot.send_message(update.effective_chat.id, "创建订单失败，请联系客服：@%s" % Admin_name)
        return

    if order:
        money = order.money
        now = order.create_time

        content = """
                    <b>充值订单创建成功，订单有效期为10分钟，请立即支付！</b>

        ➖➖➖➖➖➖➖➖➖➖
        转账地址: <code>%s</code> (TRC-20网络)
        转账金额: %s USDT 注意小数点！！！
        转账金额: %s USDT 注意小数点！！！
        转账金额: %s USDT 注意小数点！！！
        ➖➖➖➖➖➖➖➖➖➖
        请注意转账金额务必与上方的转账金额一致，否则无法自动到账
        支付完成后, 请等待1分钟左右查询，自动到账。
        订单创建时间：%s
                """ % (myaddress, money, money, money, now)
        button_list = []
        for each in ['关闭', "取消订单", '联系客服']:
            if each == '联系客服':
                button_list.append(InlineKeyboardButton(each, url="https://t.me/%s" % Admin_name))
            else:
                button_list.append(InlineKeyboardButton(each, callback_data=each))
        inline_button = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
        context.bot.send_message(update.effective_chat.id, content, parse_mode=ParseMode.HTML,
                                 reply_markup=inline_button)
        context.bot.send_message(update.effective_chat.id, content)
        dispatcher.add_handler(CallbackQueryHandler(move_order, pattern='^取消订单$'))
        return

    # 3.用户昵称
    first_name = info["from"]["first_name"]
    # 4.下单时间
    now = str(datetime.now())
    # 5.创建订单金额
    back_num = get_num()

    try:
        money = float(update.callback_query.data.replace(" USDT", ".") + back_num)
    except Exception as e:
        print("金额出错了！！")
        return
    # 我的钱包地址
    content = """
            <b>充值订单创建成功，订单有效期为10分钟，请立即支付！</b>
            
➖➖➖➖➖➖➖➖➖➖
转账地址: <code>%s</code> (TRC-20网络)
转账金额: %s USDT 注意小数点！！！
转账金额: %s USDT 注意小数点！！！
转账金额: %s USDT 注意小数点！！！
➖➖➖➖➖➖➖➖➖➖
请注意转账金额务必与上方的转账金额一致，否则无法自动到账
支付完成后, 请等待1分钟左右查询，自动到账。
订单创建时间：%s
        """ % (myaddress, money, money, money, now)
    button_list = []
    for each in ['关闭', "取消订单", '联系客服']:
        if each == '联系客服':
            button_list.append(InlineKeyboardButton(each, url="https://t.me/%s" % Admin_name))
        else:
            button_list.append(InlineKeyboardButton(each, callback_data=each))

    try:
        user = session.query(User).filter_by(t_id=t_id).first()
    except Exception as e:
        print("查询用户出错")
        context.bot.send_message(update.effective_chat.id, "创建订单失败，请联系客服：@%s" % Admin_name)
        session.close()
        return
    if not user:
        print("用户不存在")
        context.bot.send_message(update.effective_chat.id, "创建订单失败，请联系客服：@%s" % Admin_name)
        session.close()
        return

    # 将订单入库
    try:
        order = Recharge(status=2, from_address=myaddress, t_id=t_id, money=money, user_id=1, firstname=first_name)
        session.add(order)
        session.commit()
    except Exception as e:
        print("订单入库失败")
        session.rollback()
        context.bot.send_message(update.effective_chat.id, "创建订单失败，请联系客服：@toumingde")
        session.close()
        return
    inline_button = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    context.bot.send_message(update.effective_chat.id, content, parse_mode=ParseMode.HTML, reply_markup=inline_button)
    dispatcher.add_handler(CallbackQueryHandler(turn_off, pattern='^关闭$'))
    # 监听取消订单
    dispatcher.add_handler(CallbackQueryHandler(move_order, pattern='^取消订单$'))

    # 开启另一个线程，监听订单完成与否，，出发发送消息至客户中
    t1 = threading.Thread(target=listen_order, args=(order.id, update.effective_chat.id, context))
    t1.start()
    session.close()


def recharge(update, context):
    print("触发充值！")
    Group_id = global_data.get("Group_id")
    if Group_id == str(update.effective_chat.id):
        message_id = update.message.message_id
        context.bot.send_message(update.effective_chat.id, "🚫请移至机器人界面进行充值🚫", reply_to_message_id=message_id)
        return
    button_list = []
    for each in ['30 USDT', '100 USDT', '200 USDT', '500 USDT', '1000 USDT', '2000 USDT', '关闭', '联系客服']:
        if each == '联系客服':  # tg://user?id=1707841429
            button_list.append(InlineKeyboardButton(each, url="t.me/toumingde"))
        else:
            button_list.append(InlineKeyboardButton(each, callback_data=each))

    inline_button = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

    context.bot.send_message(update.effective_chat.id,
                             "—————💰萝卜充值活动💰—————\n萝卜供需初步定价为30u，充值优惠政策如下\n充值30u\n充值100u赠送50u\n充值200u赠送100u\n充值500u赠送500u\n充值1000u赠送1000u\n充值2000u赠送2000u\n——————————————\n公群老板发布供需，优惠政策  可联系客服： @toumingde\n\n 更变日期： 2023.6.1  \n\n请选择充值金额👇",
                             reply_markup=inline_button)

    dispatcher.add_handler(CallbackQueryHandler(create_order, pattern='^\d{1,} USDT$'))
    dispatcher.add_handler(CallbackQueryHandler(turn_off, pattern='^关闭$'))


def build_menu(buttons, n_cols=2, header_buttons=None, footer_buttons=None):
    """
    Returns a list of inline buttons used to generate inlinekeyboard responses

    :param buttons: `List` of InlineKeyboardButton
    :param n_cols: 设置每行按钮数
    :param header_buttons: First button value
    :param footer_buttons: Last button value
    :return: `List` of inline buttons
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def today_record(update, context):
    New_reward = global_data.get("New_reward")
    Chou = global_data.get("Chou")
    Dai_chou = global_data.get("Dai_chou")
    query = update.callback_query
    # 用户id
    info = update.callback_query.to_dict()
    t_id = info["from"]["id"]
    user_name = info["from"].get("username")
    today = datetime.now().date()
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=t_id).first()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    if not user:
        query.answer("请用/start进行注册账户！", show_alert=True)
        session.close()
        return
    user_id = user.id

    try:
        r_objs = session.query(Record).filter(Record.send_tid == user.t_id,
                                              func.cast(Record.create_time, Date) == today).all()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    # 发包支出
    zhichu = 0
    # 发包盈利
    yingli = 0
    for robj in r_objs:
        if robj.money:
            # 发包金额
            zhichu += robj.money / 100
        if robj.profit:
            # 发包盈利
            yingli += robj.profit

    # 我发包玩家中雷上级代理抽成
    lei_chou = 0
    # 我发包玩家中雷平台抽成
    pingtai_chou = 0
    try:
        sn_objs = session.query(Snatch).filter(Snatch.send_tid == user.t_id,
                                               func.cast(Snatch.create_time, Date) == today, Snatch.status == 1).all()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    for sn_obj in sn_objs:
        if user.parent:
            # # 得判断这个用户有没有上级
            lei_chou += (abs(sn_obj.profit) / 100) * Chou * Dai_chou
        pingtai_chou += (abs(sn_obj.profit) / 100) * Chou

    # 抢包收入
    snatch_shou = 0
    # 抢包中雷赔付
    snatch_lei_lose = 0
    try:
        sn_objs = session.query(Snatch).filter(Snatch.t_id == user.t_id,
                                               func.cast(Snatch.create_time, Date) == today).all()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    for sn_obj in sn_objs:
        # 抢包收入
        snatch_shou += (sn_obj.money / 100)
        if sn_obj.status == 1:
            # 抢包中雷赔付
            snatch_lei_lose += (abs(sn_obj.profit) / 100)

    # 邀请返利
    invite_money = 0
    try:
        in_objs = session.query(Holding).filter(Holding.parent == user.t_id,
                                                func.cast(Holding.create_time, Date) == today).all()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    invite_money += len(in_objs) * (New_reward / 100)

    # 下级中雷返点
    try:
        logs = session.query(Return_log).filter(Return_log.create_id == user_id,
                                                func.cast(Return_log.create_time, Date) == today).all()
    except Exception as e:
        print(e)
        query.answer("查询出错", show_alert=True)
        session.close()
        return
    low_lei_fan = 0
    for log in logs:
        low_lei_fan += int(log.money)

    content = "今日报表%s\n--------\n发包支出：-%s\n发包盈利：%s\n--------\n我发包玩家中雷上级代理抽成：-%s\n我发包玩家中雷平台抽成：-%s\n--------\n抢包收入：%s\n抢包中雷赔付：-%s\n--------\n邀请返利：%s\n下级中雷返点: %s\n--------\n" % (
        user.t_id, zhichu, yingli, round(lei_chou, 2), round(pingtai_chou, 2), round(snatch_shou, 2),
        round(snatch_lei_lose, 2), invite_money, round(low_lei_fan, 2))
    query.answer(content, show_alert=True)


def alert(update, context):
    session = Session()
    session.expire_all()
    # 用户id
    info = update.callback_query.to_dict()
    user_id = info["from"]["id"]
    query = update.callback_query
    # 根据ID查询邀请数据
    try:
        # 累计邀请
        count = session.query(Holding).filter_by(parent=user_id).count()
    except Exception as e:
        print(e)
        query.answer('查询失败', show_alert=True)
        session.close()
        return
    if not count:
        count = 0
    try:
        # 最新十条记录
        records = session.query(Holding).filter_by(parent=user_id).order_by(Holding.create_time.desc()).limit(10).all()
    except Exception as e:
        print(e)
        query.answer('查询失败', show_alert=True)
        session.close()
        return
    content = "你的id为：%s\n累计邀请：%s\n----------\n显示最后十条邀请\n----------\n" % (user_id, count)
    for obj in records:
        # 被邀请人ID
        t_id = obj.t_id
        # 邀请时间
        create_time = str(obj.create_time)[:10]
        content += "%s，用户ID：%s\n" % (create_time, t_id)
    query.answer(content, show_alert=True)


# 查看余额
def yue(update, context):
    session = Session()
    session.expire_all()
    info = update.callback_query.to_dict()
    user_id = info["from"].get("id")
    name = info["from"].get("username")
    username = name
    # 在这里添加你的回调逻辑
    query = update.callback_query
    # 根据ID查询邀请数据
    try:
        user = session.query(User).filter_by(t_id=user_id).first()
    except Exception as e:
        print(e)
        session.close()
        query.answer('查询失败', show_alert=True)
        return
    if not user:
        parent = ""
        print("邀请码为：%s" % parent)
        # 生成一个自己的邀请码
        code = get_code()
        try:
            user = User(name=username, invite_lj=code, t_id=user_id, firstname=first_name, status=1, balance=3000,
                        parent=parent)
            session.add(user)
            session.flush()
        except Exception as e:
            print(e)
            print("注册失败")
            session.close()
            return
    fistname = user.firstname
    balance = float(user.balance) / 100
    content = "%s\n%s\n---------------------------------\nID号：%s\n余额：%sU\n" % (fistname, name, user_id, balance)
    query.answer(content, show_alert=True)


def start(update, context):
    Group_name = global_data.get("Group_name")
    Group_id = global_data.get("Group_id")
    Channel_name = global_data.get("Channel_name")
    New_reward = global_data.get("New_reward")
    user_id = update.message.from_user["id"]
    username = update.message.from_user["username"]
    first_name = update.message.from_user["first_name"]
    chat_id = update.message.chat_id
    button = InlineKeyboardButton("官方群组", url="https://t.me/%s" % Group_name)
    button1 = InlineKeyboardButton("官方频道", url="https://t.me/%s" % Channel_name)
    buttons_row = [button, button1]
    keyboard = InlineKeyboardMarkup([buttons_row])
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="👏👏 欢迎 ID: %s" % user_id, reply_markup=keyboard)
    # 判断是否是新用户
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=user_id).first()
    except Exception as e:
        print(e)
        user = None
    if user:
        print("不是新用户")
        return
    # 获取 /start 命令的参数
    args = context.args
    if args:
        parent = args[0]
    else:
        parent = ""
    print("邀请码为：%s" % parent)
    if test_str(parent) or find_str(parent):
        return
    # 生成一个自己的邀请码
    code = get_code()
    try:
        new_user = User(name=username, invite_lj=code, t_id=user_id, firstname=first_name, status=1, balance=3000,
                        parent=parent)
        session.add(new_user)
        session.flush()
    except Exception as e:
        print(e)
        print("注册失败")
        session.close()
        return
    # 给上级送奖励
    try:
        p_user = session.query(User).filter_by(invite_lj=parent).first()
    except Exception as e:
        print("录入失败")
        session.close()
        p_user = ""
    if p_user:
        p_user.low += 1
        # 拉新奖励
        p_user.balance = float(p_user.balance) + New_reward
        # 添加拉新记录
        try:
            obj = Holding(parent=p_user.t_id, t_id=user_id)
        except Exception as e:
            print(e)
            obj = ""

        session.add(p_user)
        if obj:
            session.add(obj)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        session.close()
        return
    print("注册成功")
    session.close()


def send_help(update, context):
    Channel_name = global_data.get("Channel_name", "yingsheng001")
    Group_id = global_data.get("Group_id", "-1001948357949")
    Bot_name = global_data.get("Bot_name", "yinghai_bot")
    Admin_name = global_data.get("Admin_name", "toumingde")
    chat_id = update.message.chat_id
    content = """
        【1】由玩家发送发包指令，红包机器人在群内按指令发包，指令为[10-5]（机器人发送金额为 10 的红包，雷值为 5，红包数量固定6个，抢包者抢到金额的尾数是5的即中雷；
【2】用户中雷后需赔付发包者金额1.8倍即18
【3】雷值可设置1-9的任意一个数；
【4】平台抽发包者盈利的2.50%，下分提现秒到账。
【5】平台方不参与玩家的游戏盈利，全力保障公平资金安全、公平的游戏环境！
----------------------
【5】玩家发送:发包10/5,10/5,发10-5都可以
【6】玩家发送:余额、ye、查可以查看余额
【7】财务可以引用别人的话发送上分下分+金额，进行手动上下分
【8】群组将机器人设置为管理员才可以使用
【9】群组设置隐藏,用户邀请人会自动返利并成为下级用户
【10】发送/invite获取专属链接,用户通过链接加入会自动返利并成为下级用户
    """
    button = InlineKeyboardButton("客服", url="https://t.me/%s" % Admin_name)
    button1 = InlineKeyboardButton("充值", url="https://t.me/%s" % Bot_name)
    button2 = InlineKeyboardButton("玩法", url="https://t.me/%s" % Channel_name)
    button3 = InlineKeyboardButton("余额", callback_data="yue")
    # 将四个按钮放在一个列表中作为一行的按钮列表
    buttons_row = [button, button1, button2, button3]
    button4 = InlineKeyboardButton("推广查询", callback_data="promote_query")
    button5 = InlineKeyboardButton("今日报表", callback_data="today_record")
    buttons_row2 = [button4, button5]
    keyboard = InlineKeyboardMarkup([buttons_row, buttons_row2])
    dispatcher.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    dispatcher.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    dispatcher.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    context.bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=keyboard)


def invite(update, context):
    chat_id = update.message.chat_id
    # 生成带有邀请者ID参数的邀请链接
    user_id = update.message.from_user.id
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=user_id).first()
    except Exception as e:
        print(e)
        user = None
    if not user:
        update.message.reply_text(f"请使用机器人注册个人信息！ @yinghai_bot")
        return
    invite_lj = user.invite_lj
    invite_link = f"https://t.me/yinghai_bot?start={invite_lj}"
    update.message.reply_text(f"您的专属链接为: \n{invite_link}\n(用户加入自动成为您的下级用户)")


def wanfa(update, context):
    Channel_name = global_data.get("Channel_name", "yingsheng001")
    Group_id = global_data.get("Group_id", "-1001948357949")
    Bot_name = global_data.get("Bot_name", "yinghai_bot")
    Admin_name = global_data.get("Admin_name", "toumingde")
    chat_id = update.message.chat_id
    content = """
        📢红包扫雷 玩法说明
🔺随机抢包，保证绝对公平！公正！
🔺集团不参与玩家之间游戏盈利
🔺全力保障游戏、资金公平环境
🔺集团只抽发包者玩家每个雷盈利的2.50%
🔺代理可享受邀请下级会员发包盈利1.50%

最新活动：
邀请成员进群账户自动返现0.10U
下级成员发包盈利，上级返现 1.50%
        """
    button = InlineKeyboardButton("客服", url="https://t.me/%s" % Admin_name)
    button1 = InlineKeyboardButton("充值", url="https://t.me/%s" % Bot_name)
    button2 = InlineKeyboardButton("玩法", url="https://t.me/%s" % Channel_name)
    button3 = InlineKeyboardButton("余额", callback_data="yue")
    # 将四个按钮放在一个列表中作为一行的按钮列表
    buttons_row = [button, button1, button2, button3]
    button4 = InlineKeyboardButton("推广查询", callback_data="promote_query")
    button5 = InlineKeyboardButton("今日报表", callback_data="today_record")
    buttons_row2 = [button4, button5]
    keyboard = InlineKeyboardMarkup([buttons_row, buttons_row2])
    dispatcher.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    dispatcher.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    dispatcher.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    context.bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=keyboard)


def adminrecharge(update, context):
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat.id
    Admin_li = global_data.get("Admin_li")
    # 获取传递的参数
    args = context.args
    if str(user_id) not in Admin_li:
        print(user_id)
        return
    if not args:
        context.bot.send_message(chat_id=chat_id, text="模板为：/recharge 用户id 充值金额")
        return
    # 处理参数逻辑，这里只是简单地将参数打印出来
    for arg in args:
        try:
            arg = int(arg)
        except Exception as e:
            return
    t_id = args[0]
    money = int(args[1])
    if len(args) > 2:
        return
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=t_id).first()
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id, text="数据库出错")
        session.close()
        return
    print("要充值的金额为：", money)
    if money < 30 or money > 50000:
        context.bot.send_message(chat_id=chat_id, text="充值金额最少30U，最高5万U！")
        session.close()
        return
    user.balance = float(user.balance) + float(money * 100)
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        session.close()
        context.bot.send_message(chat_id=chat_id, text="充值失败")
        return
    context.bot.send_message(chat_id=chat_id,
                             text="用户：%s\ntg：%s\n充值金额：%s\n状态：成功\n账户余额为：%s" % (
                                 user.firstname, t_id, money, round(float(user.balance) / 100, 2)))
    context.bot.send_message(chat_id=t_id,
                             text="亲爱的用户：%s\n您的充值订单已完成\n金额%s已到账，请查收" % (user.firstname, money))
    session.close()


def xiafen(update, context):
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat.id
    Admin_li = global_data.get("Admin_li")
    # 获取传递的参数
    args = context.args
    if str(user_id) not in Admin_li:
        print(user_id)
        return
    if not args:
        context.bot.send_message(chat_id=chat_id, text="模板为：/xiafen 用户id 充值金额")
        return
    # 处理参数逻辑，这里只是简单地将参数打印出来
    for arg in args:
        try:
            arg = int(arg)
        except Exception as e:
            return
    t_id = args[0]
    money = int(args[1])
    if len(args) > 2:
        return
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=t_id).first()
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id, text="数据库出错")
        session.close()
        return
    print("要下分的金额为：", money)
    if money < 30 or money > 50000:
        context.bot.send_message(chat_id=chat_id, text="下分金额最少30U，最高5万U！")
        session.close()
        return
    user.balance = float(user.balance) - float(money * 100)
    try:
        w_obj = Withdrawal(user_id=user_id, t_id=t_id, money=money)
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id, text="下分失败，请联系技术人员！")
        session.close()
        return
    try:
        session.add(w_obj)
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        session.close()
        context.bot.send_message(chat_id=chat_id, text="下分失败")
        return
    context.bot.send_message(chat_id=chat_id,
                             text="用户：%s\ntg：%s\n下分金额：%s\n状态：成功\n账户余额为：%s" % (
                                 user.firstname, t_id, money, round(float(user.balance) / 100, 2)))
    session.close()


def handle_user_reply(update, context):
    Admin_group_id = global_data.get("Admin_group_id")
    Num = global_data.get("Num")
    Channel_name = global_data.get("Channel_name")
    Bei = global_data.get("Bei")
    Group_id = global_data.get("Group_id")
    Admin_name = global_data.get("Admin_name")
    # 群聊ID
    try:
        chat_id = update.message.chat_id
    except Exception as e:
        return
    if chat_id != int(Group_id):
        return
    # 发送者id
    user_id = update.message.from_user["id"]
    username = update.message.from_user["username"]
    first_name = update.message.from_user["first_name"]
    reply_text = update.message.text
    message_id = update.message.message_id
    tmp = reply_text.split("/")
    if len(tmp) != 2:
        tmp = reply_text.split("-")
    if len(tmp) != 2:
        return
    try:
        money = int(tmp[0])
        lei = int(tmp[1])
    except Exception as e:
        return
    if money < 5 or money > 5000:
        context.bot.send_message(chat_id, "🚫发包失败，发包金额范围5-5000🚫", reply_to_message_id=message_id)
        return
    if lei < 0 or lei > 9:
        return
    session = Session()
    session.expire_all()
    try:
        user = session.query(User).filter_by(t_id=user_id).first()
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id, "🚫发包失败🚫", reply_to_message_id=message_id)
        session.close()
        return
    if not user:
        # 生成一个自己的邀请码
        code = get_code()
        try:
            user = User(name=username, invite_lj=code, t_id=user_id, firstname=first_name, status=1, balance=3000)
            session.add(user)
            session.flush()
        except Exception as e:
            print(e)
            session.rollback()
            session.close()
            return
    if (float(user.balance) / 100) < money:
        # reply_to_message_id=message_id
        context.bot.send_message(chat_id, "🚫您的余额已不足发包,当前余额:%s" % (float(user.balance) / 100),
                                 reply_to_message_id=message_id)
        return
    user.balance = str(float(user.balance) - (money * 100))

    result = distribute_red_packet(money * 100, Num)
    lei_number = 0
    for line in result:
        if str(line)[-1] == str(lei):
            lei_number += 1
    # 创建红包记录
    try:
        record = Record(send_tid=user.t_id, money=money * 100, bei=Bei, num=Num, residue=Num,
                        result=json.dumps(result), lei=lei, lei_number=lei_number, firstname=first_name)
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id, "🚫发包失败🚫", reply_to_message_id=message_id)
        return
    session.add(record)
    session.flush()
    if lei_number > 0:
        lei_status = "💣雷"
    else:
        lei_status = "💵"
    photo_path = 'img/upic.jpg'
    print("""[ %s ] 发了个%s U红包!.""" % (first_name, money))
    context.bot.send_message(Admin_group_id,
                             """%s[ %s ] 发了个%s U红包!\n踩雷数字为：%s.\n当前红包是否有雷：%s\n预计开包结果为：%s""" % (
                                 lei_status, first_name, money, lei, lei_status, result))
    content = """[ <code>%s</code> ] 发了个%s U红包,快来抢!.""" % (first_name, money)
    # 抢红包按钮
    rob_btn = InlineKeyboardButton("🧧抢红包[%s/0]总%sU 雷%s" % (Num, money, lei),
                                   callback_data='rob_%s_%s_%s_%s' % (record.id, money, lei, 1))
    button = InlineKeyboardButton("客服", url="https://t.me/%s" % Admin_name)
    button1 = InlineKeyboardButton("充值", url="https://t.me/%s" % Admin_name)
    button2 = InlineKeyboardButton("玩法", url="https://t.me/%s" % Channel_name)
    button3 = InlineKeyboardButton("余额", callback_data="yue")
    buttons_row1 = [rob_btn]
    # 将四个按钮放在一个列表中作为一行的按钮列表
    buttons_row2 = [button, button1, button2, button3]
    button4 = InlineKeyboardButton("推广查询", callback_data="promote_query")
    button5 = InlineKeyboardButton("今日报表", callback_data="today_record")
    buttons_row3 = [button4, button5]
    keyboard = InlineKeyboardMarkup([buttons_row1, buttons_row2, buttons_row3])
    dispatcher.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    dispatcher.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    dispatcher.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    # 第一个是记录ID
    # 第二个是红包金额
    # 第三个是雷
    # 第四个表示第几个红包
    dispatcher.add_handler(CallbackQueryHandler(rob, pattern='^rob_%s_%s_%s_%s' % (record.id, money, lei, 1)))
    try:
        session.add(user)
        session.commit()
        context.bot.send_photo(chat_id, caption=content, photo=open(photo_path, 'rb'), reply_to_message_id=message_id,
                               parse_mode=ParseMode.HTML, reply_markup=keyboard)
    except Exception as e:
        print(e)
        session.rollback()
        session.close()
        context.bot.send_message(chat_id, "🚫发包失败🚫", reply_to_message_id=message_id)
        return


def update_env(update, content):
    global global_data
    # 读取数据库配置信息
    session = Session()
    session.expire_all()
    try:
        objs = session.query(Conf).all()
    except Exception as e:
        print(e)
        session.close()
        return
    for obj in objs:
        if obj.typestr == "float":
            value = float(obj.value)
            print(value)
            print(obj.typestr)
        elif obj.typestr == "list":
            value = json.loads(obj.value)
        elif obj.typestr == "int":
            value = int(obj.value)
        elif obj.typestr == "str":
            value = str(obj.value)
        else:
            value = obj.value
        global_data[obj.name] = value


def today_data(update, context):
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat.id
    Admin_li = global_data.get("Admin_li")
    Chou = float(global_data.get("Chou", 0.025))
    if str(user_id) not in Admin_li:
        print(user_id)
        return
    session = Session()
    session.expire_all()
    # 获取今天的日期
    today_date = date.today()

    try:
        r_objs = session.query(Record).filter(func.DATE(Record.create_time) == today_date).all()
    except Exception as e:
        print(e)
        return
    # 1.今日总发包金额、总抽水金额
    today_fa_money = 0
    today_chou = 0
    for r_obj in r_objs:
        fa_money = r_obj.money / 100
        today_fa_money += fa_money
        today_chou += (fa_money * Chou) + (fa_money * float(r_obj.bei) * r_obj.lei_number * Chou)
    # 4.今日充值金额、今日充值笔数
    today_recharge_money = 0
    today_recharge_num = 0
    try:
        charge_objs = session.query(Recharge).filter(func.DATE(Recharge.create_time) == today_date,
                                                     Recharge.status == 1).all()
    except Exception as e:
        print(e)
        return
    for c_obj in charge_objs:
        today_recharge_money += c_obj.money
        today_recharge_num += 1
    # 5.今日提现金额、今日提现笔数
    today_withdrawal_money = 0
    today_withdrawal_num = 0
    print(today_date)
    try:
        drawal_objs = session.query(Withdrawal).filter(func.DATE(Withdrawal.create_time) == today_date).all()
    except Exception as e:
        print(e)
        return
    for d_obj in drawal_objs:
        today_withdrawal_money += float(d_obj.money)
        today_withdrawal_num += 1

    context.bot.send_message(chat_id=chat_id,
                             text="今日总发包金额：%s\n今日总抽水金额：%s\n今日充值金额：%s\n今日充值笔数：%s\n今日提现金额：%s\n今日提现笔数：%s" % (
                                 today_fa_money, today_chou, today_recharge_money, today_recharge_num,
                                 today_withdrawal_money, today_withdrawal_num))
    session.close()


# 用户命令功能
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', send_help))
dispatcher.add_handler(CommandHandler('invite', invite))
dispatcher.add_handler(CommandHandler('wanfa', wanfa))
# 管理员命令功能
dispatcher.add_handler(CommandHandler('adminrecharge', adminrecharge))
dispatcher.add_handler(CommandHandler('recharge', recharge))
dispatcher.add_handler(CommandHandler('xiafen', xiafen))
dispatcher.add_handler(CommandHandler('update', update_env))
dispatcher.add_handler(CommandHandler('today', today_data))
# 监听发红包
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_reply))

if __name__ == '__main__':
    print('开始运行机器人.....')
try:
    updater.start_polling()
    updater.idle()
except KeyboardInterrupt:
    updater.stop()

