import discord
from discord.ext import commands
import youtube_dl

bot = commands.Bot(command_prefix="!", description="kaspairBot")
musics = {}
ytdl = youtube_dl.YoutubeDL()


def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)


@bot.event
async def on_ready():
    print("Ready !")


class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download = False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]


@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []


@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()


@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()


@bot.command()
async def commandbot(ctx):
    await ctx.send("Tu veut de l'aide ? !play 'ton lien'  !leave !pause !serverInfo !skip")


@bot.command()
async def coucou(ctx):
    await ctx.send("Coucou !")


@bot.command()
async def serverInfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    serverDescription = server.description
    numberOfPerson = server.member_count
    serverName = server.name
    message = f"Le serveur **{serverName}** contient *{numberOfPerson}* personnes ! \nLa description du serveur est {serverDescription}. \nCe serveur possède {numberOfTextChannels} salons écrit et {numberOfVoiceChannels} salon vocaux."
    await ctx.send(message)


@bot.command()
async def ras(ctx, *text):
    chineseChar = "丹书匚刀巳下呂廾工丿片乚爪冂口尸Q尺丂丁凵V山乂Y乙"
    chineseText = []
    for word in text:
        for char in word:
            if char.isalpha():
                index = ord(char) - ord("a")
                transformed = chineseChar[index]
                chineseText.append(transformed)
            else:
                chineseText.append(char)
        chineseText.append(" ")
    await ctx.send("".join(chineseText))


@bot.command()
async def kick(ctx, user: discord.User, *reason):
    reason = " ".join(reason)
    await ctx.guild.kick(user, reason=reason)
    await ctx.send(f"{user} à été kick.")


@bot.command()
async def clear(ctx, nombre: int):
    messages = await ctx.channel.history(limit=nombre + 1).flatten()
    for message in messages:
        await message.delete()


@bot.command()
async def play(ctx, url):
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance : {video.url}")
        play_song(client, musics[ctx.guild], video)


bot.run("*****************************")
