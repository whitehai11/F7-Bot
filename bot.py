import discord
from discord.ext import commands, tasks
import asyncio

# Dein Bot-Token
TOKEN = 'MTM2MjkzMzM1NTEyMDk1NTUxMg.GM4NDZ.UdbMY35_vHtHX-G6LOR9QgtRDRZ8QLtPdqktC0'

# Bot-Intents und Prefix
intents = discord.Intents.default()
intents.members = True  # Erforderlich für Mitglieder-Events
intents.message_content = True  # Um Nachrichten zu überwachen

bot = commands.Bot(command_prefix='!', intents=intents)

# ID des Server (Guild)
GUILD_ID = 1345497471358468268  # Ersetze durch die tatsächliche ID deines Servers

# Kanalnamen
ONLINE_CHANNEL_NAME = 'online-users'
F7_CHANNEL_NAME = 'f7-clan-members'
BOTS_CHANNEL_NAME = 'bots-members'

# Event, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f'{bot.user} ist online!')
    await create_stat_channels()

# Funktion, um die Kanäle zu erstellen (oder sicherzustellen, dass sie existieren)
async def create_stat_channels():
    guild = bot.get_guild(GUILD_ID)

    # Versuche, die Kanäle zu finden
    online_channel = discord.utils.get(guild.text_channels, name=ONLINE_CHANNEL_NAME)
    f7_channel = discord.utils.get(guild.text_channels, name=F7_CHANNEL_NAME)
    bots_channel = discord.utils.get(guild.text_channels, name=BOTS_CHANNEL_NAME)

    # Falls der Kanal nicht existiert, erstelle ihn
    if not online_channel:
        online_channel = await guild.create_text_channel(ONLINE_CHANNEL_NAME)
    if not f7_channel:
        f7_channel = await guild.create_text_channel(F7_CHANNEL_NAME)
    if not bots_channel:
        bots_channel = await guild.create_text_channel(BOTS_CHANNEL_NAME)

    # Setze die Kanalberechtigungen, damit niemand in den Kanälen schreiben kann
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False)  # Niemand kann Nachrichten senden
    }
    
    # Wende die Berechtigungen auf die Kanäle an
    await online_channel.edit(overwrites=overwrites)
    await f7_channel.edit(overwrites=overwrites)
    await bots_channel.edit(overwrites=overwrites)

    # Starte die Aktualisierung der Statistiken
    update_stats.start(online_channel, f7_channel, bots_channel)

# Task, der alle 5 Minuten die Kanäle aktualisiert
@tasks.loop(minutes=5)
async def update_stats(online_channel, f7_channel, bots_channel):
    guild = bot.get_guild(GUILD_ID)

    # Zähle die Mitglieder
    online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
    f7_members = sum(1 for member in guild.members if 'F7 Clan member' in [role.name for role in member.roles])
    bot_members = sum(1 for member in guild.members if 'BOT' in [role.name for role in member.roles])

    # Aktualisiere die Kanäle mit den aktuellen Statistiken
    await online_channel.edit(name=f"Online Users: {online_members}")
    await f7_channel.edit(name=f"F7 Clan Members: {f7_members}")
    await bots_channel.edit(name=f"Bots: {bot_members}")

# Moderations-Befehle
@bot.command()
@commands.has_permissions(manage_messages=True)
async def timeout(ctx, member: discord.Member, seconds: int):
    """Setzt einen Timeout für einen Benutzer"""
    await member.timeout(seconds=seconds)
    await ctx.send(f'{member.name} wurde für {seconds} Sekunden timeoutet!')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    """Kickt einen Benutzer vom Server"""
    await member.kick()
    await ctx.send(f'{member.name} wurde vom Server gekickt!')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    """Bannt einen Benutzer vom Server"""
    await member.ban()
    await ctx.send(f'{member.name} wurde vom Server gebannt!')

# Fortnite-Stats Befehl
@bot.command()
async def fortnitestats(ctx, username: str):
    """Zeigt Fortnite-Stats eines Spielers"""
    url = f'https://api.fortnitetracker.com/v1/profile/{username}'
    headers = {'TRN-Api-Key': '4bd20cd0-f5e5-4f20-8d6e-11c16bb6c6e6'}  # Ersetze mit deinem Fortnite API-Key
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        kda = stats['kda']
        wins = stats['wins']
        kills = stats['kills']
        await ctx.send(f'{username} - K/D: {kda}, Wins: {wins}, Kills: {kills}')
    else:
        await ctx.send(f'Fehler beim Abrufen der Stats für {username}!')

# Fortnite-Shop Befehl
@bot.command()
async def fortniteshop(ctx):
    """Zeigt die aktuellen Items im Fortnite-Shop"""
    url = 'https://api.fortnitetracker.com/v1/shop'
    headers = {'TRN-Api-Key': 'DE4bd20cd0-f5e5-4f20-8d6e-11c16bb6c6e6'}  # Ersetze mit deinem Fortnite API-Key
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        shop_items = response.json()
        shop_message = "Aktueller Fortnite-Shop:\n"
        
        for item in shop_items:
            name = item['name']
            price = item['price']
            shop_message += f'{name} - {price} V-Bucks\n'
        
        await ctx.send(shop_message)
    else:
        await ctx.send('Fehler beim Abrufen des Fortnite-Shops!')

# Bot starten
bot.run(TOKEN)
