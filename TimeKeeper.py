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
    try:
        fomatedDate = datetime.datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        await ctx.send("Lỗi nhập sai ngày")
        return

    if((datetime.datetime.now() - fomatedDate).days > 1):
        await ctx.send("Lỗi ngày nghỉ không hợp lệ")
        return

    if(ctx.channel.id != ANNOUNCEMENTS_ID):
        await ctx.send("Sang channel anncoucements để xin nghỉ nhoa")
        return
    else:
        try:
            await ctx.send("{} Xin nghỉ {} ngày: {} với lý do: {}".format(ctx.author.name, part_of_day, date, reason))
            sh = gc.open_by_key(SHEET_KEY)
            wks = sh.worksheet_by_title(
                "{}/{}".format(fomatedDate.month, fomatedDate.year))
            row = wks.find(ctx.author.name)[0].row
            col = wks.find(
                "{}/{}/{}".format(fomatedDate.month, fomatedDate.day, fomatedDate.year))[0].col
            value = "nghỉ "
            if (part_of_day == 'sáng' or part_of_day == 'chiều'):
                value += "1/2"
            wks.update_value((row, col), value)

            if(fomatedDate.weekday() >= 5):
                wks.cell((row, col)).color = (121/255, 50/255, 168/255)
            elif(part_of_day == 'sáng' or part_of_day == 'chiều'):
                 wks.cell((row, col)).color = (3/255, 162/255, 252/255)
            else:
                wks.cell((row, col)).color = (189/255, 64/255, 55/255)

            wks.cell((row, col)).set_text_format('bold', True).set_text_format('fontSize', 12).set_text_format(
                'foregroundColor', (1, 1, 1, 1))
        except Exception as ex:
            await ctx.send("Lỗi rồi xin nghỉ lại đi!!!!")

client.run(DISCORD_BOT_KEY)
