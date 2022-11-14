import asyncio,discord
from PyYTMusic import PyYTMusic

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
        if interaction.message.interaction.user == interaction.user:
          voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
          if voice.is_playing():
              voice.pause()
              embed = interaction.message.embeds[0].to_dict()
              embed['title'] = "Song is paused"
              embed = discord.Embed.from_dict(embed)
              await interaction.response.edit_message(embed=embed)
          elif voice.is_paused():
              voice.resume()
              embed = interaction.message.embeds[0].to_dict()
              embed['title'] = "Song is playing"
              embed = discord.Embed.from_dict(embed)
              await interaction.response.edit_message(embed=embed)
        else:
          await interaction.response.send_message(content="You cannot use buttons other than the person using the command", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="✖️")
    async def destroy_button_callback(self, button, interaction):
      if interaction.message.interaction.user == interaction.user:
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        await voice.disconnect()
      else:
        await interaction.response.send_message(content="You cannot use buttons other than the person using the command", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Lyrics")
    async def lyrics_button_callback(self, button, interaction):
      if button.style == discord.ButtonStyle.primary:
        embed = interaction.message.embeds[0]
        self.children[-1].style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(embed=embed,view=self)
        await self.msg.delete()
        await interaction.response.defer()
      else:
        embed = interaction.message.embeds[0]
        embed_ = embed.to_dict()
        name = embed_['description'].split("- ")[1]
        browse_id = embed_['footer']['text'].split("browseId: ")[1]
        lyrics = ytmusic.lyrics(name, browse_id)['result']
        embed_ = discord.Embed(description=lyrics, color=0x00ff00)
        self.children[-1].style = discord.ButtonStyle.primary
        await interaction.response.edit_message(embed=embed,view=self)
        msg = await interaction.followup.send(embed=embed_)
        self.msg = msg
        
@bot.event
async def on_ready():
    print("Ready!")

@bot.command(description="Show all available commands")
async def commands(ctx):
    embed = discord.Embed(title="Help",description="**All Commands**",color=0x3498db)
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
        embed = discord.Embed(description="You are not on the voice channel", color=0x3498db)
        return await ctx.respond(embed=embed)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        if voice_state.channel.id == voice.channel.id:
            embed = discord.Embed(title="A song is currently playing", color=0x00ff00)
            return await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="I'm already connected to another voice channel.", color=0x3498db)
            return await ctx.respond(embed=embed)
    embed = discord.Embed(title="🔎 Searching", color=0x00ff00)
    message = await ctx.respond(embed=embed)
    results = ytmusic.search(song_name, ['songs'], limit=1)['results'][0]       
    embed = discord.Embed(title="Currently playing song",description=f"{results['author']} - {results['name']}",color=0x00ff00).set_thumbnail(url=results['thumbnails'][0]['url']).set_footer(text=f"browseId: {results['browseId']}")
    await message.edit_original_response(embed=embed, view=View(timeout=None))
    channel = voice_state.channel
    vc = await channel.connect()
    def after_disconnect(error):
      disconnect = vc.disconnect()
      disconnect_await = asyncio.run_coroutine_threadsafe(disconnect, bot.loop)
      delete = message.delete_original_response()
      delete_await = asyncio.run_coroutine_threadsafe(delete, bot.loop)
      disconnect_await.result()
      delete_await.result()
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
    embed = discord.Embed(description="Deleting messages...", color=0x3498db)
    await ctx.respond(embed=embed)
    await ctx.channel.purge(limit=None, check=check)
    
@bot.command(description="bot server info")
async def server_info(ctx):
  await ctx.respond('\n'.join(guild.name for guild in bot.guilds))

token = os.getenv("TOKEN")
bot.run(token)
