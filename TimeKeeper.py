from http import client
from discord_slash import SlashCommand, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_choice, create_option
import pygsheets
import datetime

SHEET_KEY = "1Inz2N5Oy5wxoBK0NI173qfPeQwAU2OtcORR5lf67uOg"
DISCORD_BOT_KEY = "OTY0ODEwNDEzNTk2MzY0ODIw.YlqDtw.GF9RXBe7BbGeIB523GiSBbOPTm8"
ANNOUNCEMENTS_ID = 964809316370620416
DISCORD_SERVER_ID = [964747347802345493]

# authorization sheet
gc = pygsheets.authorize(service_file='CredentialTimeKeeperKey.json')

client = commands.Bot(command_prefix='!')

slash = SlashCommand(client, sync_commands=True)


@slash.slash(
    name="xin_nghi",
    description="Xin nghỉ phép",
    guild_ids=DISCORD_SERVER_ID,
    options=[
        create_option(
            name="date",
            description="Ngày nghỉ",
            required=True,
            option_type=3,
        ),
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
            name="reason",
            description="Lý do nghỉ",
            option_type=3,
            required=True,
        )
    ]
)
async def xin_nghi(ctx: SlashContext, date: str, part_of_day: str, reason: str):
    if(ctx.channel.id != ANNOUNCEMENTS_ID):
        await ctx.send("Sang channel announcements để xin nghỉ")
        return
    current_date = datetime.datetime.now()
    current_year = current_date.year
    try:
        input_date = datetime.datetime.strptime(date, '%d/%m')
        if(current_date.month == 12 and input_date.month == 1):
            current_year += 1
            input_date = input_date.replace(year=current_year)
    except ValueError:
        await ctx.send("Lỗi nhập sai ngày: Nhập ngày với định dạng d/m")
        return

    if((current_date - input_date).days > 0):
        await ctx.send("Lỗi ngày nghỉ không hợp lệ")
        return

    try:
        sh = gc.open_by_key(SHEET_KEY)
        wks = sh.worksheet_by_title(
            "{}/{}".format(input_date.month, input_date.year))
        row = wks.find("{}".format(ctx.author.id))[0].row
        col = wks.find(
            "{}/{}/{}".format(input_date.month, input_date.day, input_date.year))[0].col
        value = "nghỉ "
        if (part_of_day == 'sáng' or part_of_day == 'chiều'):
            value += "1/2"
        wks.update_value((row, col), value)
        await ctx.send("{} Xin nghỉ {} ngày: {} với lý do: {}".format(ctx.author.name, part_of_day, date, reason))
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
    current_date = datetime.datetime.now()
    current_year = current_date.year
    try:
        from_date = datetime.datetime.strptime(from_date, "%d/%m")
        to_date = datetime.datetime.strptime(to_date, "%d/%m")
        if(current_date.month == 12 and input_date.month == 1):
            current_year += 1
        input_date = input_date.replace(year=current_year)
    except ValueError:
        await ctx.send("Lỗi fomat ngày hoặc ngày trong quá khứ")
        return

    if((current_date - from_date).days > 0 or (current_date - to_date).days > 0 or (from_date - to_date).days >= 0):
        await ctx.send("Lỗi nhập sai ngày bắt đầu hoặc kết thúc {}".format(ctx.author.id))
        return

    await ctx.send("Xinnnnnn {}".format(ctx.author.id))
client.run(DISCORD_BOT_KEY)
