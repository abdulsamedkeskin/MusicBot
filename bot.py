import os
import requests,asyncio,discord
from discord.ext import bridge

intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(command_prefix="!", intents=intents)

api_url = "https://MusicStream.sametkeskin.repl.co/get-music"

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

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏹️")
    async def stop_button_callback(self, button, interaction):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        voice.stop()
        embed = interaction.message.embeds[0].to_dict()
        embed['title'] = "Şarkı Durduruldu"
        embed = discord.Embed.from_dict(embed)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="✖️")
    async def destroy_button_callback(self, button, interaction):
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        await voice.disconnect()
        await interaction.response.delete_message()

@bot.event
async def on_ready():
    print("Ready!")

@bot.bridge_command(description="Show all available commands")
async def commands(ctx):
    embed = discord.Embed(title="Yardım",
                          description="**Bütün Kodlar**",
                          color=0x3498db)
    embed.add_field(name="!hi", value="Bot will say hi")
    embed.add_field(name="!clear", value="Delete messages on server\n")
    embed.add_field(
        name="!play",
        value=
        "Allows you to search for the song.You have to react to play the song\n",
        inline=False)
    await ctx.respond(embed=embed)


@bot.bridge_command(description="Bot will say hi")
async def hi(ctx):
    await ctx.respond(f"Hi <@{ctx.author.id}>")


@bot.bridge_command(description="Play a song")
async def play(ctx, song_name: str):
    voice_state = ctx.author.voice
    if voice_state is None:
        embed = discord.Embed(description="Ses kanalında değilsiniz",
                              color=0x3498db)
        return await ctx.respond(embed=embed)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        if voice.is_playing():
            if voice_state.channel.id == voice.channel.id:
                embed = discord.Embed(title="Şu anda zaten bir şarkı çalınıyor",color=0x00ff00)
                return await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Zaten başka bir odaya bağlıyım.",
                              color=0x3498db)
            return await ctx.respond(embed=embed)           
    embed = embed = discord.Embed(title="🔎 Aranıyor",color=0x00ff00)
    message = await ctx.respond(embed=embed)
    data = {"query": song_name}
    request = requests.post(api_url, json=data)
    response = request.json()
    channel = voice_state.channel
    embed = discord.Embed(title="Şu anda oynatılan şarkı",
                        description=f"{response['title']}",
                        color=0x00ff00).set_thumbnail(
                            url=response['thumbnail'])
    vc = await channel.connect()
    await message.edit_original_message(embed=embed, view=View())
    vc.play(discord.FFmpegPCMAudio(**FFMPEG_OPTIONS,source=response['url']), after=lambda e: vc.disconnect())
    while vc.is_playing():
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(15)
        while vc.is_playing():
            break
        else:
            await vc.disconnect()
            await message.delete_original_message()

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state and len(voice_state.channel.members) == 1:
      return await voice_state.disconnect()

@bot.bridge_command(description="Delete messages on server")
async def clear(ctx):
    embed = discord.Embed(description="Mesajlar Siliniyor...", color=0x3498db)
    await ctx.respond(embed=embed)
    await ctx.channel.purge(limit=None)

token = os.getenv("TOKEN")
bot.run(token)
