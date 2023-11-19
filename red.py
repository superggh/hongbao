import asyncio
import telegram
from telegram.constants import ParseMode
from datetime import datetime, date

import logging

from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup,BotCommand
from telegram.ext import filters,Updater,ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Group_name = "Group_name"
    Channel_name = "Channel_name"
    user_id = update.message.from_user["id"]
    username = update.message.from_user["username"]
    first_name = update.message.from_user["first_name"]
    chat_id = update.message.chat_id
    button = InlineKeyboardButton("官方群组", url="https://t.me/%s" % Group_name)
    button1 = InlineKeyboardButton("官方频道", url="https://t.me/%s" % Channel_name)
    buttons_row = [button, button1]
    keyboard = InlineKeyboardMarkup([buttons_row])
    await context.bot.send_message(chat_id=update.message.chat_id,
                             text="👏👏 欢迎 ID: %s" % user_id, reply_markup=keyboard)
    args = context.args
    if args:
            parent = args[0]
    else:
        parent = ""
    print("邀请码为：%s" % parent)


async def handle_user_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handle_user_reply")
    chat_id = update.message.chat_id
    # 发送者id
    Num = 6
    Admin_name = "Admin_name"
    Channel_name = "Channel_name"
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
        await context.bot.send_message(chat_id, "🚫发包失败，发包金额范围5-5000🚫", reply_to_message_id=message_id)
        return
    if lei < 0 or lei > 9:
        return
    user = {"balance":10000}
    if (float(user["balance"]) / 100) < money:
        # reply_to_message_id=message_id
        await context.bot.send_message(chat_id, "🚫您的余额已不足发包,当前余额:%s" % (float(user["balance"]) / 100),
                                 reply_to_message_id=message_id)
        return
    user["balance"] = str(float(user["balance"]) - (money * 100))
    # result = distribute_red_packet(money * 100, Num)
    lei_number = 0

    if lei_number > 0:
        lei_status = "💣雷"
    else:
        lei_status = "💵"
    photo_path = 'bg.jpg'
    result = []
    record = {"id":1}
  
    print("""[ %s ] 发了个%s U红包!.""" % (first_name, money))
    await context.bot.send_message(chat_id,
                             """%s[ %s ] 发了个%s U红包!\n踩雷数字为：%s.\n当前红包是否有雷：%s\n预计开包结果为：%s""" % (
                                 lei_status, first_name, money, lei, lei_status, result))
    content = """[ <code>%s</code> ] 发了个%s U红包,快来抢!.""" % (first_name, money)
    # 抢红包按钮
    rob_btn = InlineKeyboardButton("🧧抢红包[%s/0]总%sU 雷%s" % (Num, money, lei),
                                   callback_data='rob_%s_%s_%s_%s' % (record['id'], money, lei, 1))
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
    application.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    application.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    application.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    # 第一个是记录ID
    # 第二个是红包金额
    # 第三个是雷
    # 第四个表示第几个红包
    application.add_handler(CallbackQueryHandler(rob, pattern='^rob_%s_%s_%s_%s' % (record["id"], money, lei, 1)))
    await context.bot.send_photo(chat_id, caption=content, photo=open(photo_path, 'rb'), reply_to_message_id=message_id,
                               parse_mode=ParseMode.HTML, reply_markup=keyboard)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def rob(update,context):
    print('rob')
    query = update.callback_query
    info = update.callback_query.to_dict()
    user_id = info["from"].get("id")
    name = info["from"].get("username")
    print(user_id,name)
    content = "您已经抢过该红包了! \n"
    await query.answer(content, show_alert=True)

async def today_record(update, context):
    query = update.callback_query
    info = update.callback_query.to_dict()
    t_id = info["from"]["id"]
    user_name = info["from"].get("username")
    today = datetime.now().date()
    zhichu = -10
    yingli = 999
    lei_chou = 10
    pingtai_chou = 5
    snatch_shou = 100
    snatch_lei_lose = -10
    invite_money = 0
    low_lei_fan = 0
    content = "今日报表%s\n--------\n发包支出：-%s\n发包盈利：%s\n--------\n我发包玩家中雷上级代理抽成：-%s\n我发包玩家中雷平台抽成：-%s\n--------\n抢包收入：%s\n抢包中雷赔付：-%s\n--------\n邀请返利：%s\n下级中雷返点: %s\n--------\n" % (
        t_id, zhichu, yingli, round(lei_chou, 2), round(pingtai_chou, 2), round(snatch_shou, 2),
        round(snatch_lei_lose, 2), invite_money, round(low_lei_fan, 2))
    await query.answer(content, show_alert=True)


async def alert(update,context):
    info = update.callback_query.to_dict()
    user_id = info["from"].get("id")
    name = info["from"].get("username")
    username = name
    # 在这里添加你的回调逻辑
    query = update.callback_query
    fistname = "user.firstname"
    count = 0
    content = "你的id为：%s\n累计邀请：%s\n----------\n显示最后十条邀请\n----------\n" % (user_id, count)
    await query.answer(content, show_alert=True)

# 查看余额
async def yue(update, context):
 
    # session = Session()
    # session.expire_all()
    info = update.callback_query.to_dict()
    user_id = info["from"].get("id")
    name = info["from"].get("username")
    username = name
    # 在这里添加你的回调逻辑
    query = update.callback_query
    # 根据ID查询邀请数据
    try:
        # user = session.query(User).filter_by(t_id=user_id).first()
        user = "aaa"
    except Exception as e:
        print(e)
        # session.close()
        query.answer('查询失败', show_alert=True)
        return
    if not user:
        parent = ""
        print("邀请码为：%s" % parent)
        # 生成一个自己的邀请码
        # code = get_code()
        code = "aaa"
        try:
            print('try')
            # user = User(name=username, invite_lj=code, t_id=user_id, firstname=first_name, status=1, balance=3000,
            #             parent=parent)
            # session.add(user)
            # session.flush()
        except Exception as e:
            print(e)
            print("注册失败")
            # session.close()
            return

    balance = float(10000) / 100
    content = "%s\n---------------------------------\nID号：%s\n余额：%sU\n" % ( name, user_id, balance)
    await query.answer(content, show_alert=True)


async def invite(update, context):
  
    chat_id = update.message.chat_id
    # 生成带有邀请者ID参数的邀请链接
    user_id = update.message.from_user.id
 
    try:
        user = "1"
    except Exception as e:
        print(e)
        user = None
    if not user:
        await update.message.reply_text(f"请使用机器人注册个人信息！ @redpock_bot")
        return
    # invite_lj = user.invite_lj
    invite_lj = "asdfef"
    invite_link = f"https://t.me/redpock_bot?start={invite_lj}"
    await update.message.reply_text(f"您的专属链接为: \n{invite_link}\n(用户加入自动成为您的下级用户)")

async def wanfa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('wanfa')
    Channel_name = "channelname"
    Group_id = "123"
    Bot_name ="botname"
    Admin_name = "adminname"
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
    application.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    application.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    application.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    await context.bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=keyboard)


async def send_help(update, context):
    Channel_name = "Channel_name"
    Group_id = ""
    Bot_name = "botname"
    Admin_name = "adminname"
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
    application.add_handler(CallbackQueryHandler(alert, pattern='^promote_query'))
    application.add_handler(CallbackQueryHandler(today_record, pattern='^today_record'))
    application.add_handler(CallbackQueryHandler(yue, pattern='^yue'))
    await context.bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=keyboard)



if __name__ == '__main__':
    commands = [
        BotCommand(command="start", description="开始使用机器人"),
        BotCommand(command="invite", description="创建邀请链接"),
        BotCommand(command="help", description="帮助信息"),
        BotCommand(command="recharge", description="自动充值"),
        BotCommand(command="wanfa", description="玩法"),
    ]

    application = ApplicationBuilder().token('6388824981:AAGLOdFPszKUVV9hkh-ino6B0lZ3FpASHSI').build()
    application.bot.set_my_commands(commands)
 
    # 监听发红包
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_reply)
    application.add_handler(echo_handler)
    # 用户命令功能
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', send_help))
    application.add_handler(CommandHandler('invite', invite))
    application.add_handler(CommandHandler('wanfa', wanfa))

    application.run_polling()

# async def main():
 
#     bot = telegram.Bot("6388824981:AAGLOdFPszKUVV9hkh-ino6B0lZ3FpASHSI")
#     async with bot:
#         print(await bot.get_me())
#         print((await bot.get_updates())[0])
#         first_name = "aaa"
#         money = 1
#         chat_id = 5176890779
#         photo_path = 'bg.jpg'
#         print("""[ %s ] 发了个%s U红包!.""" % (first_name, money))

#         content = """[ <code>%s</code> ] 发了个%s U红包,快来抢!.""" % (first_name, money)
#         await bot.send_photo(chat_id, caption=content, photo=open(photo_path, 'rb'),  
#                                parse_mode=ParseMode.HTML )
#         await bot.send_message(5176890779,
#                                 """%s[ %s ] 发了个%s U红包!\n踩雷数字为：%s.\n当前红包是否有雷：%s\n预计开包结果为：%s""" % (
#                                     "111", first_name, money, "1", "2", "4"))
#         content = """[ <code>%s</code> ] 发了个%s U红包,快来抢!.""" % (first_name, money)
#         # await bot.send_message(text='Hi John!', chat_id=5176890779)

# if __name__ == '__main__':
#     asyncio.run(main())