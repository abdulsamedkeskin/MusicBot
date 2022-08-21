import os
import asyncio,discord,aiohttp
from PyYTMusic import PyYTMusic

ytmusic = PyYTMusic()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
application_id = os.getenv('application_id')

FFMPEG_OPTIONS = {
    'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',   
}

class View(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯️")
    async def play_pause_button_callback(self, button, interaction):
        if interaction.message.interaction.user == interaction.user:
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
        else:
          await interaction.response.send_message(content="Komutu kullanan kişi dışında butonları kullanamazsınız", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="✖️")
    async def destroy_button_callback(self, button, interaction):
      if interaction.message.interaction.user == interaction.user:
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        await voice.disconnect()
      else:
        await interaction.response.send_message(content="Komutu kullanan kişi dışında butonları kullanamazsınız", ephemeral=True)


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
        embed = discord.Embed(description="Ses kanalında değilsiniz", color=0x3498db)
        return await ctx.respond(embed=embed)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        if voice_state.channel.id == voice.channel.id:
            embed = discord.Embed(
                title="Şu anda zaten bir şarkı çalınıyor", color=0x00ff00)
            return await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Zaten başka bir odaya bağlıyım.", color=0x3498db)
            return await ctx.respond(embed=embed)
    embed = discord.Embed(title="🔎 Aranıyor", color=0x00ff00)
    message = await ctx.respond(embed=embed)
    results = ytmusic.search(song_name, ['songs'], limit=1)['results'][0]
    name = results['name']
    browse_id = results['browseId']
    lyrics_button = discord.ui.Button(
        style=discord.ButtonStyle.primary, label="Lyrics on/off")
    lyric = {"on": False}
    async def delete_interaction_response():
      try:
       async with aiohttp.ClientSession() as client:
        async with client.delete(f"https://discord.com/api/v10/webhooks/{application_id}/{lyric['token']}/messages/@original") as response:
            await response.text()
            await client.close()
        lyric['on'] = False
      except:
        print("An error occured")
    async def lyrics_button_callback(interaction):
        if lyric['on'] is False:
            lyrics = ytmusic.lyrics(name, browse_id)['result']
            embed = discord.Embed(description=lyrics, color=0x00ff00)
            msg = await interaction.response.send_message(embed=embed)
            lyric['on'] = True
            lyric['token'] = msg.token
        else:
            await delete_interaction_response()
            await interaction.response.defer()
    lyrics_button.callback = lyrics_button_callback
    embed = discord.Embed(title="Şu anda oynatılan şarkı",
                          description=f"{results['author']} - {results['name']}",
                          color=0x00ff00).set_thumbnail(
        url=results['thumbnails'][0]['url'])
    await message.edit_original_message(embed=embed, view=View(lyrics_button, timeout=None))
    channel = voice_state.channel
    vc = await channel.connect()
    def after_disconnect(error):
      disconnect = vc.disconnect()
      disconnect_await = asyncio.run_coroutine_threadsafe(disconnect, bot.loop)
      delete = message.delete_original_message()
      delete_await = asyncio.run_coroutine_threadsafe(delete, bot.loop)
      delete_lyrics = delete_interaction_response()
      delete_lyrics_await = asyncio.run_coroutine_threadsafe(delete_lyrics, bot.loop)
      try:
        disconnect_await.result()
        delete_await.result()
        delete_lyrics_await.result()
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
    def check(m):
      if m.author == bot.user:
        if not m.components:
          return True
        return False
      return True      
    embed = discord.Embed(description="Mesajlar Siliniyor...", color=0x3498db)
    await ctx.respond(embed=embed)
    await ctx.channel.purge(limit=None, check=check)

token = os.getenv("TOKEN")
bot.run(token)
