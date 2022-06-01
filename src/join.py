import discord

async def show_welcome(member, entrance_channel, register_channel):
    guild = member.guild
    e_channel = None
    r_channel = None

    for channel in guild.channels:
        if channel.name == entrance_channel:
            e_channel = channel
        elif channel.name == register_channel:
            r_channel = channel

    if e_channel != None and r_channel != None :
        await e_channel.send(f"<@{member.id}>歡迎~ 記得到<#{r_channel.id}>登記身分組喔~")
