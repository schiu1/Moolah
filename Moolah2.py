import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

#have a copy of the client_secret.json specific to your google sheet API in same directory as this file
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gs_client = gspread.authorize(creds)

#name of google sheet and specific worksheet here
sheet = gs_client.open('').worksheet('')

#creates the discord client connection and sets the prefix to call the commands
Client = discord.Client()
client = commands.Bot(command_prefix = "!")
client.remove_command("help")

reset = False

#used to find the column in the sheet that item would be recorded on
#ex. all shells would be recorded in the 4th column of the google sheet
itemCol = {"shells": 4,
           "skins": 5,
           "horns": 6,
           "jawbones": 7,
           "spikes": 8,
           "neidans": 9,
           "coins": 10,
           "goblets": 11,
           "steel": 12,
           "whiskers": 13,
           "fins": 14,
           "tongues": 15,
           "amethysts": 16
           }

@client.event
async def on_ready():
    print("Bot is ready!")

#adds items to the records tied to the user in the sheet
@client.command(pass_context=True)
async def add(ctx, item, amount):
    global itemCol
    if ctx.message.author.id == client.user.id:
        return
    global reset
    if reset is True:
        global creds
        global gs_client
        global sheet
        gs_client = gspread.authorize(creds)
        #google sheet and specific worksheet
        sheet = gs_client.open('').worksheet('')
        reset = False

    userID = ctx.message.author.id
    if creds.access_token_expired:
        gs_client.login()
        print("refreshed")
    try:
        cell = sheet.find(userID)
    except:
        await client.send_message(ctx.message.channel, "<@%s>" % (userID))
        desc = "**User not found.** :poop: \n Please contact an Officer or Leo to add you to the list. :nerd:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
    userRow = int(cell.row)
    userCol = 0
    if item in itemCol:
        userCol = itemCol[item]
    else:
        await client.send_message(ctx.message.channel, "<@%s> Unknown Item" % (userID))
        return

    oldAmt = sheet.cell(userRow, userCol).value.replace(",", "")
    amount = amount.replace(",", "")
    if oldAmt == "":
        newAmt = float(amount)
    else:
        newAmt = float(oldAmt) + float(amount)

    sheet.update_cell(userRow, userCol, newAmt)
    emote = ""
    RGB = 0
    if item == "shells":
        emote = ":shell:"
        RGB = 0xFFFFFF
    if item == "skins":
        emote = ":fish:"
        RGB = 0x00FFFF
    if item == "horns":
        emote = ":rhino:"
        RGB = 0x808080
    if item == "jawbones":
        emote = ":dragon_face:"
        RGB = 0x000000
    if item == "spikes":
        emote = ":shrimp:"
        RGB = 0xFF00FF
    if item == "neidans":
        emote = ":rosette:"
        RGB = 0x0000FF
    if item == "coins":
        emote = ":medal:"
        RGB = 0xFFFF00
    if item == "goblets":
        emote = ":trophy:"
        RGB = 0xFFFF00
    if item == "steel":
        emote = ":pick:"
        RGB = 0xFFFFFF
    if item == "whiskers":
        emote = ":mouse:"
        RGB = 0x00FFFF
    if item == "fins":
        emote = ":shark:"
        RGB = 0x808080
    if item == "tongues":
        emote = ":tongue:"
        RGB = 0x000000
    if item == "amethysts":
        emote = ":crown:"
        RGB = 0xFF00FF
    result = sheet.cell(userRow, userCol).value
    await client.send_message(ctx.message.channel, "<@%s>" % (userID))
    desc = "Added %s %s!\n**Your Total:** %s %s. %s" % (amount, item, result, item, emote)
    embed = discord.Embed(description=desc, color=RGB)
    await client.send_message(ctx.message.channel, embed=embed)

#allows user to give a specified number of loot to another user
@client.command(pass_context=True)
async def give(ctx, item, amount, reciever):
    global itemCol
    if ctx.message.author.id == client.user.id:
        return
    global reset
    if reset is True:
        global creds
        global gs_client
        global sheet
        gs_client = gspread.authorize(creds)
        #google sheet and specific worksheet
        sheet = gs_client.open('').worksheet('')
        reset = False
    if creds.access_token_expired:
        gs_client.login()
        print("refreshed")

    senderID = ctx.message.author.id
    try:
        cell = sheet.find(senderID)
    except:
        await client.send_message(ctx.message.channel, "<@%s>" % (userID))
        desc = "**User not found.** :poop: \n Please contact an Officer or Leo to add you to the list. :nerd:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
    senderRow = int(cell.row)

    userCol = 0

    if item in itemCol:
        userCol = itemCol[item]
    else:
        await client.send_message(ctx.message.channel, "<@%s>"  % (senderID))
        desc = "**Unknown Item.** :shrug:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
        return
    oldAmt = sheet.cell(senderRow, userCol).value.replace(",", "")
    print(oldAmt)
    amount = amount.replace(",", "")
    print(amount)
    if oldAmt == "":
        newAmt = float(amount)
    elif float(oldAmt) < float(amount):
        await client.send_message(ctx.message.channel, "<@%s>" % (senderID))
        desc = "**Insufficient Amount.** :no_entry_sign:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
        return
    else:
        newAmt = float(oldAmt) - float(amount)
    sheet.update_cell(senderRow, userCol, newAmt)

    for ch in ["<", ">", "!", "@"]:
        if ch in reciever:
            reciever = reciever.replace(ch, "")
    recInfo = await client.get_user_info(reciever)
    recName = recInfo.name + "#" + recInfo.discriminator
    try:
        cell = sheet.find(reciever)
    except:
        await client.send_message(ctx.message.channel, "<@%s>" % (userID))
        desc = "**User not found.** :poop: \n Please contact an Officer or Leo to add you to the list. :nerd:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
    recRow = int(cell.row)
    oldAmt = sheet.cell(recRow, userCol).value.replace(",", "")
    if oldAmt == "":
        newAmt = float(amount)
    else:
        newAmt = float(oldAmt) + float(amount)
    sheet.update_cell(recRow, userCol, newAmt)
    emote = ""
    if item == "shells":
        emote = ":shell:"
    if item == "skins":
        emote = ":fish:"
    if item == "horns":
        emote = ":rhino:"
    if item == "jawbones":
        emote = ":dragon_face:"
    if item == "spikes":
        emote = ":shrimp:"
    if item == "neidans":
        emote = ":rosette:"
    if item == "coins":
        emote = ":medal:"
    if item == "goblets":
        emote = ":trophy:"
    if item == "steel":
        emote = ":pick:"
    if item == "whiskers":
        emote = ":mouse:"
    if item == "fins":
        emote = ":shark:"
    if item == "tongues":
        emote = ":tongue:"
    if item == "amethysts":
        emote = ":crown:"
    sResult = sheet.cell(senderRow, userCol).value
    rResult = sheet.cell(recRow, userCol).value
    await client.send_message(ctx.message.channel, "<@%s>" % (senderID))
    desc = "__Gave %s %s to %s.__ :heart:\n**Your total:** %s %s. %s\n**%s's total:** %s %s. %s" % (amount, item, recName, sResult, item, emote, recName, rResult, item, emote)
    embed = discord.Embed(description=desc, color=0xFFC0CB)
    await client.send_message(ctx.message.channel, embed=embed)

#shows the total silver made for a specified user
@client.command(pass_context = True)
async def total(ctx, user):
    if ctx.message.author.id == client.user.id:
        return
    global reset
    if reset is True:
        global creds
        global gs_client
        global sheet
        gs_client = gspread.authorize(creds)
        #google sheet and specific worksheet
        sheet = gs_client.open('').worksheet('')
        reset = False

    userID = ctx.message.author.id
    if creds.access_token_expired:
        gs_client.login()
        print("refreshed")

    for ch in ["<",">","!","@"]:
        if ch in user:
            user = user.replace(ch, "")
    userInfo = await client.get_user_info(user)
    targetName = userInfo.name+"#"+userInfo.discriminator

    try:
        cell = sheet.find(user)
    except:
        await client.send_message(ctx.message.channel, "<@%s>" % (userID))
        desc = "**User not found.** :poop: \n Please contact an Officer or Leo to add you to the list. :nerd:"
        embed = discord.Embed(description=desc, color=0x800000)
        await client.send_message(ctx.message.channel, embed=embed)
    userRow = int(cell.row)

    result = sheet.cell(userRow, 17).value
    percent = sheet.cell(userRow, 3).value
    await client.send_message(ctx.message.channel, "<@%s>" % (userID))
    desc = "**%s's Total:** \n %s silver *(%s of 700mil)*. :moneybag:" % (targetName, result, percent)
    embed = discord.Embed(description=desc, color=0x008000)
    await client.send_message(ctx.message.channel, embed=embed)

#assigns a specified role for those that reached the quota from SMH loot (set at 1 million silver)
@client.command(pass_context = True)
@commands.has_role("Officer")
async def assign(ctx):
    startTime = time.time()
    #id of server bot is on and role to assign
    server = client.get_server(id="")
    role = get(server.roles, id="")
    discordList = list(server.members)
    sheetList = sheet.get_all_values()
    sheetList.pop(0)
    embed = discord.Embed(
        description="All changes to SMH role distribution",
        color=0xFFC0CB
    )
    for person in sheetList:
        personInfo = ""
        for mem in discordList:
            if mem.id == person[0]:
                personInfo = mem
                break
        name = personInfo.name+"#"+personInfo.discriminator
        rolesList = personInfo.roles
        roleIds = []
        for i in rolesList:
            roleIds.append(i.id)
        total = float(person[16].replace(",", ""))
        if (total >= 100000000.00 and "" not in roleIds): #"" is roleid to assign
            print("adding")
            await client.add_roles(personInfo, role)
            embed.add_field(name="**%s**" % (name), value="Gave SMH Role", inline=True)
        elif (total < 100000000.00 and "" in roleIds): #"" is roleid to assign
            print("removing")
            await client.remove_roles(personInfo, role)
            embed.add_field(name="**%s**" % (name), value="Removed SMH Role", inline=True)
    await client.send_message(ctx.message.channel, embed=embed)
    endTime = time.time() - startTime
    print("done assigning, "+str(endTime)+" seconds")

#displays all commands available for this bot
@client.command(pass_context = True)
async def help(ctx):
    userID = ctx.message.author.id
    await client.send_message(ctx.message.channel, "<@%s> :pray:" % (userID))
    desc = ":shell: !add shells # = Candidum Shells \n:fish: !add skins # = Ocean Stalker Skins \n:rhino: !add horns # = Nineshark's Horn Fragment \n:dragon_face: !add jawbones # = Black Rust's Jawbone \n:shrimp: !add spikes # = Hekaru's Spike \n:rosette: !add neidans # = Neidans \n:medal: !add coins # = Golden Coins \n:trophy: !add goblets # = Golden Goblets \n:pick: !add steel # = Steel Candidum Shells \n:mouse: !add whiskers # = Ocean Stalker Whiskers \n:shark: !add fins # = Nineshark's Fins \n:tongue: !add tongues # = Black Rust's Tongues \n:crown: !add amethysts # = Amethyst Hekaru Spikes \n:heart: !give item # @User = Give loot to another member \n:moneybag: !total @User = View user's total made silver for the week"
    embed = discord.Embed(description=desc, color=0xFFA500)
    await client.send_message(ctx.message.channel, embed=embed)

#starts up and keeps the bot running
while True:
    print('entering infinite loop')
    loop = asyncio.get_event_loop()
    try:
        print('trying')
        loop.run_until_complete(client.start("")) #discord bot token
        print('run complete')
    except BaseException as e:
        print('error: ', e)
        reset = True
        time.sleep(5)
