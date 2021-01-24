import discord
from discord.errors import ClientException
import youtube_dl
from discord.utils import get
from discord.ext import commands,tasks
import asyncio

client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print('Bot is on ready')


ydl_opts = {
    'format': 'bestaudio/best',
    'default_search': 'ytsearch',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'noplaylist': True,
}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@client.event
async def on_message(message):
    if message.author.bot == False:
        try:
            ctx = message.content.split("!")[1]
        except IndexError:
            ctx = 'a b'
        if ctx == "hi":
            await message.channel.send(f'Merhaba {message.author.name}')
        if ctx == "clear":
            embed = discord.Embed(description="Mesajlar Siliniyor...", color=0x3498db)
            await message.channel.send(embed=embed)
            await message.channel.purge(limit=None)
        if ctx == "help":
            embed = discord.Embed(title="Yardım", description="**Bütün Kodlar**", color=0x3498db)
            embed.add_field(name="!hi",value="Bot greet you")
            embed.add_field(name="!clear",value="Delete messages on server\n")
            embed.add_field(name="!play", value="Allows you to search for the song.You have to react to play the song\n", inline=False)
            embed.add_field(name="\n\n!pause",value="\nPauses the song")
            embed.add_field(name="!resume",value="Resume the song")
            embed.add_field(name="!stop",value="Stop the song")
            embed.add_field(name="!destroy",value="Bot exit voice channel\n")
            await message.channel.send(embed=embed)
        if ctx.split()[0] == "play":
            if message.author.voice and message.author.voice.channel:
                channel = message.author.voice.channel
                try:
                    await channel.connect()
                except ClientException:
                    pass
                if ctx.find("play ") != -1:
                    embed = discord.Embed(description="**Şarkı Aranıyor...**", color=0x00ff00)
                    bot_message = await message.channel.send(embed=embed)
                    search = ""
                    for i in ctx.split()[1:]:
                        search_word = ''.join(i)
                        search += " " + search_word
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        video = ydl.extract_info(f"ytsearch5:{search}", download=False)
                    results = video['entries']
                    if results != [""]:
                        result = [i['title'] for i in results]
                        embed_result = ""
                        for i in result:
                            embed_result += f"\n**{result.index(i) + 1}.**   {i}"
                        embedVar = discord.Embed(title="Sonuçlar", description=embed_result, color=0x00ff00)
                        await bot_message.edit(embed=embedVar)
                        await bot_message.add_reaction("1\uFE0F\u20E3")
                        await bot_message.add_reaction("2\uFE0F\u20E3")
                        await bot_message.add_reaction("3\uFE0F\u20E3")
                        await bot_message.add_reaction("4\uFE0F\u20E3")
                        await bot_message.add_reaction("5\uFE0F\u20E3")
                    def check(reaction, user):
                        return user == message.author and (str(reaction.emoji) == "1\uFE0F\u20E3" or str(
                            reaction.emoji) == "2\uFE0F\u20E3" or str(reaction.emoji) == "3\uFE0F\u20E3" or str(
                            reaction.emoji) == "4\uFE0F\u20E3" or str(reaction.emoji) == "5\uFE0F\u20E3")
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=10.0,check=check)
                    except asyncio.TimeoutError:
                        reaction =""
                    selection_check = str(reaction)
                    server = message.guild
                    voice_channel = server.voice_client
                    if selection_check == "1\uFE0F\u20E3":
                        source = results[0]['url']
                        voice_channel.play(discord.FFmpegPCMAudio(source=source, **FFMPEG_OPTIONS))
                        embed = discord.Embed(title="Şu anda oynatılan şarkı", description=f"{results[0]['title']}",
                                              color=0x00ff00).set_thumbnail(url=results[0]['thumbnail'])
                        await message.channel.send(embed=embed)
                    if selection_check == "2\uFE0F\u20E3":
                        source = results[1]['url']
                        voice_channel.play(discord.FFmpegPCMAudio(source=source, **FFMPEG_OPTIONS))
                        embed = discord.Embed(title="Şu anda oynatılan şarkı", description=f"{results[1]['title']}",
                                              color=0x00ff00).set_thumbnail(url=results[1]['thumbnail'])
                        await message.channel.send(embed=embed)
                    if selection_check == "3\uFE0F\u20E3":
                        source = results[2]['url']
                        voice_channel.play(discord.FFmpegPCMAudio(source=source, **FFMPEG_OPTIONS))
                        embed = discord.Embed(title="Şu anda oynatılan şarkı", description=f"{results[2]['title']}",
                                              color=0x00ff00).set_thumbnail(url=results[2]['thumbnail'])
                        await message.channel.send(embed=embed)
                    if selection_check == "4\uFE0F\u20E3":
                        source = results[3]['url']
                        voice_channel.play(discord.FFmpegPCMAudio(source=source, **FFMPEG_OPTIONS))
                        embed = discord.Embed(title="Şu anda oynatılan şarkı", description=f"{results[3]['title']}",
                                              color=0x00ff00).set_thumbnail(url=results[3]['thumbnail'])
                        await message.channel.send(embed=embed)
                    if selection_check == "5\uFE0F\u20E3":
                        source = results[4]['url']
                        voice_channel.play(discord.FFmpegPCMAudio(source=source, **FFMPEG_OPTIONS))
                        embed = discord.Embed(title="Şu anda oynatılan şarkı", description=f"{results[4]['title']}",
                                              color=0x00ff00).set_thumbnail(url=results[4]['thumbnail'])
                        await message.channel.send(embed=embed)
                    voice = get(client.voice_clients, guild=message.guild)
                    while voice.is_playing():
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(15)
                        while voice.is_playing():
                            break
                        else:
                            await voice.disconnect()
                else:
                    embed = discord.Embed(description="Lütfen şarkının ismini de girin", color=0x00ff00)
                    await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description="Lütfen bir ses kanalına girin", color=0x00ff00)
                await message.channel.send(embed=embed)
        if ctx == "pause":
            voice = get(client.voice_clients, guild=message.guild)
            if voice and voice.is_playing():
                voice.pause()
                embed = discord.Embed(description="Şarkı duraklatıldı.", color=0x00ff00)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description="Şarkıl duraklatılamadı.", color=0x00ff00)
                await message.channel.send(embed=embed)
        if ctx == "resume":
            voice = get(client.voice_clients, guild=message.guild)
            if voice and voice.is_paused():
                voice.resume()
                embed = discord.Embed(description="Şarkı devam ettiriliyor.", color=0x00ff00)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description="Şarkı devam ettirilemiyor", color=0x00ff00)
                await message.channel.send(embed=embed)
        if ctx == "stop":
            voice = get(client.voice_clients, guild=message.guild)
            if voice and voice.is_playing():
                voice.stop()
                embed = discord.Embed(description="Şarkı durduruldu.", color=0x00ff00)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description="Şarkı durdurulamadı.", color=0x00ff00)
                await message.channel.send(embed=embed)
        if ctx == "destroy":
            voice = get(client.voice_clients, guild=message.guild)
            if voice:
                await voice.disconnect()
            else:
                embed = discord.Embed(description="Bir hata meydana geldi", color=0x00ff00)
                await message.channel.send(embed=embed)
        @tasks.loop(seconds=2.0)
        async def check_voice():
            voice = get(client.voice_clients, guild=message.guild)
            try:
                member_count = len(voice.members)
            except:
                member_count=[]
            if member_count == 1:
                await voice.disconnect()
                return True
        check_voice.start()
token = "your token here"

client.run(token)
