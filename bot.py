import os
import asyncio,discord
from PyYTMusic import PyYTMusic
from keep_alive import keep_alive

ytmusic = PyYTMusic()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

FFMPEG_OPTIONS = {
    'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',   
}

class View(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯️")
    async def play_pause_button_callback(self, button, interaction):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            voice.pause()
            embed = interaction.message.embeds[0].to_dict()
            embed['title'] = "Şarkı Duraklatıldı"
            embed = discord.Embed.from_dict(embed)
            await interaction.response.edit_message(embed=embed)
        elif voice.is_paused():
            voice.resume()
            embed = interaction.message.embeds[0].to_dict()
            embed['title'] = "Şarkı Devam Ediyor"
            embed = discord.Embed.from_dict(embed)
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="✖️")
    async def destroy_button_callback(self, button, interaction):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        await voice.disconnect()
        embed=discord.Embed(title="Şarkı Kapatıldı",color=0x00ff00)
        await interaction.response.edit_message(embed=embed)


@bot.event
async def on_ready():
    print("Ready!")


@bot.command(description="Show all available commands")
async def commands(ctx):
    embed = discord.Embed(title="Yardım",description="**Bütün Kodlar**",color=0x3498db)
    embed.add_field(name="/hi", value="Will say hi")
    embed.add_field(name="/clear", value="Delete all messages on channel\n")
    embed.add_field(name="/play song_name",value="Play a song\n",inline=False)
    await ctx.respond(embed=embed)


@bot.command(description="Bot will say hi")
async def hi(ctx):
    await ctx.respond(f"Hi <@{ctx.author.id}>")


@bot.command(description="Play a song")
async def play(ctx, song_name: str):
    voice_state = ctx.author.voice
    if voice_state is None:
        embed = discord.Embed(description="Ses kanalında değilsiniz",color=0x3498db)
        return await ctx.respond(embed=embed)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        if voice.is_playing():
            if voice_state.channel.id == voice.channel.id:
                embed = discord.Embed(title="Şu anda zaten bir şarkı çalınıyor",color=0x00ff00)
                return await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Zaten başka bir odaya bağlıyım.",color=0x3498db)
            return await ctx.respond(embed=embed)           
    embed = discord.Embed(title="🔎 Aranıyor",color=0x00ff00)
    message = await ctx.respond(embed=embed)
    results = ytmusic.search(song_name)['results'][0]
    channel = voice_state.channel
    embed = discord.Embed(title="Şu anda oynatılan şarkı",
                        description=f"{results['author']} - {results['name']}",
                        color=0x00ff00).set_thumbnail(
                            url=results['thumbnails'][0]['url'])
    vc = await channel.connect()
    await message.edit_original_message(embed=embed, view=View(timeout=None))
    def after_disconnect(error):
      disconnect = vc.disconnect()
      disconnect_await = asyncio.run_coroutine_threadsafe(disconnect, bot.loop)
      delete = message.delete_original_message()
      delete_await = asyncio.run_coroutine_threadsafe(delete, bot.loop)
      try:
        disconnect_await.result()
        delete_await.result()
      except:
        pass
    vc.play(discord.FFmpegPCMAudio(**FFMPEG_OPTIONS,source=results['playerUrl']), after=after_disconnect)

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state and len(voice_state.channel.members) == 1:
      return await voice_state.disconnect()

@bot.command(description="Delete messages on server")
async def clear(ctx):
    embed = discord.Embed(description="Mesajlar Siliniyor...", color=0x3498db)
    await ctx.respond(embed=embed)
    await ctx.channel.purge(limit=None)

token = os.getenv("TOKEN")
bot.run(token)
