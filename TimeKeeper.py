from http import client
from discord_slash import SlashCommand, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_choice, create_option
import pygsheets
from datetime import datetime, timedelta
import json

SHEET_KEY = "1Inz2N5Oy5wxoBK0NI173qfPeQwAU2OtcORR5lf67uOg"
DISCORD_BOT_KEY = "OTY0ODEwNDEzNTk2MzY0ODIw.YlqDtw.2Bi5kCkksFno5fY9vfMXdtIgFyg"
ANNOUNCEMENTS_ID = 964809316370620416
DISCORD_SERVER_ID = [964747347802345493]
WEEK_DAY = ["thứ hai", "thứ ba", "thứ tư",
            "thứ năm", "thứ sáu", "thứ bảy", "chủ nhật"]

# authorization sheet
gc = pygsheets.authorize(service_file='CredentialTimeKeeperKey.json')
sh = gc.open_by_key(SHEET_KEY)

client = commands.Bot(command_prefix='!')

slash = SlashCommand(client, sync_commands=True)


@slash.slash(
    name="xin_nghi",
    description="Xin nghỉ phép",
    guild_ids=DISCORD_SERVER_ID,
    options=[
        create_option(
            name="part_of_day",
            description="Chọn buổi nghỉ",
            required=True,
            option_type=3,
            choices=[
                create_choice(
                    name="Sáng!",
                    value="sáng"
                ),
                create_choice(
                    name="Chiều!",
                    value="chiều"
                ),
                create_choice(
                    name="Cả ngày!",
                    value="cả"
                )
            ]
        ),
        create_option(
            name="date",
            description="Ngày nghỉ",
            required=True,
            option_type=3,
        ),

        create_option(
            name="reason",
            description="Lý do nghỉ",
            option_type=3,
            required=True,
        )
    ]
)
async def xin_nghi(ctx: SlashContext, part_of_day: str, date: str, reason: str):
    if(ctx.channel.id != ANNOUNCEMENTS_ID):
        await ctx.send("Sang channel announcements để xin nghỉ")
        return
    current_date = datetime.now()
    current_year = current_date.year
    try:
        input_date = datetime.strptime(date, '%d/%m')
        if(current_date.month == 12 and input_date.month == 1):
            current_year += 1
        input_date = input_date.replace(year=current_year)
    except ValueError:
        await ctx.send("Lỗi nhập sai ngày: Nhập ngày với định dạng ngày/tháng")
        return

    if((current_date - input_date).days > 0):
        await ctx.send("Lỗi! Xin nghỉ ngày trong quá khứ mất tiêu")
        return

    if(input_date.weekday() == 6):
        await ctx.send("Xin nghỉ vào chủ nhật ư vip!!!")
        return

    try:
        await ctx.send("{} Xin nghỉ {} {} ngày: {} với lý do: {}".format(ctx.author.name, part_of_day, WEEK_DAY[input_date.weekday()], date, reason))

        wks = sh.worksheet_by_title(
            "{}/{}".format(input_date.month, input_date.year))
        row = wks.find("{}".format(ctx.author.id))[0].row
        print("{}/{}/{}".format(input_date.month, input_date.day, input_date.year))
        col = wks.find("{}/{}/{}".format(input_date.month,
                       input_date.day, input_date.year))[0].col
        print("row {}, col {}".format(row, col))
        value = "nghỉ "
        if (part_of_day == 'sáng' or part_of_day == 'chiều'):
            value += "1/2"
        wks.update_value((row, col), value)

    except Exception as ex:
        print(ex)
        await ctx.send("Lỗi rồi xin nghỉ lại đi!!!!")


@slash.slash(
    name="xin_nghi_nhieu_ngay",
    description="xin nghỉ nhiều ngày",
    guild_ids=DISCORD_SERVER_ID,
    options=[

        create_option(
            name="from_part_of_day",
            description="từ buổi",
            option_type=3,
            required=True,
            choices=[
                create_choice(
                    name="Chiều!",
                    value="chiều"
                ),
                create_choice(
                    name="Cả ngày!",
                    value="cả"
                )
            ]
        ),

        create_option(
            name="from_date",
            description="ngày",
            option_type=3,
            required=True,
        ),

        create_option(
            name="to_part_of_day",
            description="tới buổi",
            option_type=3,
            required=True,
            choices=[
                create_choice(
                    name="Sáng!",
                    value="sáng"
                ),
                create_choice(
                    name="Cả ngày!",
                    value="cả"
                )
            ]
        ),

        create_option(
            name="to_date",
            description="ngày",
            option_type=3,
            required=True
        ),

        create_option(
            name="reason",
            description="lý do nghỉ",
            option_type=3,
            required=True
        ),

    ]
)
async def xin_nghi_nhieu_ngay(ctx: SlashContext, from_part_of_day: str, from_date: str, to_part_of_day: str, to_date: str, reason):
    if(ctx.channel.id != ANNOUNCEMENTS_ID):
        await ctx.send("Sang channel announcements để xin nghỉ")
        return
    current_date = datetime.now()
    current_year = current_date.year
    try:
        if(from_date.count(from_date) <= 5):
            from_date = datetime.strptime(from_date, "%d/%m")
            to_date = datetime.strptime(to_date, "%d/%m")
            if(current_date.month == 12 and from_date.month != 12):
                next_year = current_year + 1
                from_date = from_date.replace(year=next_year)
                to_date = to_date.replace(year=next_year)
            elif(current_date.month == 12 and to_date.month != 12):
                next_year = current_year + 1
                from_date = from_date.replace(year=current_year)
                to_date = to_date.replace(year=next_year)
            else:
                from_date = from_date.replace(year=current_year)
                to_date = to_date.replace(year=current_year)
        else:
            from_date = datetime.strptime(from_date, "%d/%m/%y")
            to_date = datetime.strptime(to_date, "%d/%m/%y")
        print("{}->{}".format(from_date, to_date))

    except ValueError:
        await ctx.send("Lỗi fomat ngày hoặc ngày trong quá khứ")
        return

    if((current_date - from_date).days > 0 or (current_date - to_date).days > 0 or (from_date - to_date).days >= 0):
        await ctx.send("Lỗi nhập sai ngày bắt đầu hoặc kết thúc {}".format(ctx.author.id))
        return

    try:
        await ctx.send("{} Xin nghỉ từ {} {} ngày: {} tới {} {} ngày: {} với lý do: {}".format(ctx.author.name, from_part_of_day, WEEK_DAY[from_date.weekday()], from_date.strftime('%d/%m'), to_part_of_day, WEEK_DAY[to_date.weekday()], to_date.strftime('%d/%m'), reason))
        if(from_date.month == to_date.month):
            on_leave_in_month(ctx, from_part_of_day,
                              from_date, to_part_of_day, to_date)
        else:
            on_leave_multi_month(ctx, from_part_of_day,
                                 from_date, to_part_of_day, to_date)
    except ValueError:
        await ctx.send("Lỗi rồi! Hãy xin nghỉ lại")


@slash.slash(
    name="list_ngay_nghi",
    description="Xem ngày đã nghỉ",
    guild_ids=DISCORD_SERVER_ID,
    options=[
        create_option(
            name="month",
            description="ngày nghỉ trong tháng",
            option_type=3,
            required=True,
        )
    ]

)
async def list_ngay_da_nghi(ctx: SlashContext, month: str):
    await ctx.send("{} đã xem số buổi nghỉ trong tháng {}".format(ctx.author.name, month))
    wks = sh.worksheet_by_title(
        "{}/{}".format(month, datetime.now().year))
    first_day_of_month = datetime.now()
    print(first_day_of_month)
    first_day_of_month = first_day_of_month.replace(
        year=datetime.now().year, month=int(month), day=1)
    current_date = first_day_of_month
    row = wks.find("{}".format(ctx.author.id))[0].row
    data = wks.get_row(row)
    data = data[3:]
    i = 0
    count = 0
    res = "Tháng {} {} đã nghỉ những ngày: \n".format(month, ctx.author.name)
    for item in data:
        if(item != ""):
            count += 1
            res += "{} : {} \n".format(current_date.strftime('%d/%m'), item)
        i += 1
        current_date = first_day_of_month + timedelta(i)
    if(count == 0):
        res = "Tháng {} {} không nghỉ ngày nào".format(month, ctx.author.name)
    await ctx.author.send(res)


def on_leave_in_month(ctx, from_part_of_day, from_date, to_part_of_day, to_date):
    wks = sh.worksheet_by_title(
        "{}/{}".format(from_date.month, from_date.year))
    row = wks.find("{}".format(ctx.author.id))[0].row
    col = wks.find("{}/{}/{}".format(from_date.month,
                                     from_date.day, from_date.year))[0].col
    value = "nghỉ"
    if(from_part_of_day == "chiều"):
        value += " 1/2"
    wks.update_value((row, col), value)
    count_day = (to_date - from_date).days
    if(count_day > 1):
        for i in range(1, count_day):
            check_date = from_date + timedelta(days=i)
            if(check_date.weekday() == 6):
                continue
            col += 1
            value = "nghỉ"
            wks.update_value((row, col), value)
    col += 1
    value = "nghỉ"
    if(to_part_of_day == "sáng"):
        value += " 1/2"
    wks.update_value((row, col), value)


def on_leave_multi_month(ctx, from_part_of_day, from_date, to_part_of_day, to_date):
    wks = sh.worksheet_by_title(
        "{}/{}".format(from_date.month, from_date.year))
    row = wks.find("{}".format(ctx.author.id))[0].row
    col = wks.find("{}/{}/{}".format(from_date.month,
                                     from_date.day, from_date.year))[0].col
    value = "nghỉ"
    if(from_part_of_day == "chiều"):
        value += " 1/2"
    wks.update_value((row, col), value)
    count_day = (to_date - from_date).days
    if(count_day > 1):
        for i in range(1, count_day):
            check_date = from_date + timedelta(days=i)
            if(check_date.weekday() == 6):
                continue
            wks = sh.worksheet_by_title(
                "{}/{}".format(check_date.month, check_date.year))
            row = wks.find("{}".format(ctx.author.id))[0].row
            col = wks.find(
                "{}/{}/{}".format(check_date.month, check_date.day, check_date.year))[0].col
            value = "nghỉ"
            wks.update_value((row, col), value)
    wks = sh.worksheet_by_title(
        "{}/{}".format(to_date.month, to_date.year))
    row = wks.find("{}".format(ctx.author.id))[0].row
    col = wks.find("{}/{}/{}".format(to_date.month,
                                     to_date.day, to_date.year))[0].col
    value = "nghỉ"
    if(to_part_of_day == "sáng"):
        value += " 1/2"
    wks.update_value((row, col), value)


client.run(DISCORD_BOT_KEY)
