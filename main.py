import discord
from discord.ext import commands
from datetime import datetime
from colorama import Fore, init
from pystyle import Center
import os
import json
import ctypes
config = json.load(open("config.json", encoding="utf-8"))
init()
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def title():
    if os.name == "nt":
        ctypes.windll.kernel32.SetConsoleTitleW(f"Vouchme | .gg/multiboosts")
    else:
        pass

def load_vouch_count():
    if os.path.exists("vouch_count.json"):
        with open("vouch_count.json", "r") as f:
            return json.load(f).get("vouch_count", 1)
    return 1

def save_vouch_count(count):
    with open("vouch_count.json", "w") as f:
        json.dump({"vouch_count": count}, f)

vouch_count = load_vouch_count()

embed_color = int(config['hex_embed_color'], 16)
server = config["support_server"]
footertext = config["footer_text"]
activity = discord.Activity(type=discord.ActivityType.playing, name=config['status'])
bot = discord.Bot(command_prefix="/", activity=activity, status=discord.Status.online, intents=discord.Intents.all())

@bot.slash_command(name='vouch', stars=int, description='Give a vouch to someone!', guild_ids=[int(config['guild_id'])])
async def vouch(ctx, message: str, stars = discord.Option(str, "select how many stars", choices=['⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐', '⭐']), attachment = discord.Option(discord.Attachment, "upload image/video proof", required=False)):
    channeltosend = await bot.fetch_channel(int(config['vouch_command_channel']))
    await ctx.defer()
    global vouch_count
    
    user = ctx.user
    current_date = datetime.now().strftime("%Y-%m-%d")
    stars_count = stars.count('⭐')
    time = datetime.utcnow()

    embed = discord.Embed(title="Thank you for your vouch!", color=embed_color, url=server)
    embed.add_field(name="Vouch:", value=message, inline=False)
    embed.add_field(name="Stars:", value=stars, inline=False)
    embed.add_field(name="Nº:", value=vouch_count, inline=True)
    embed.add_field(name="Vouched on:", value=current_date, inline=True)
    embed.add_field(name="Vouched by:", value=f"{user.mention}", inline=True)
    embed.set_footer(text=footertext)
    embed.timestamp = time
    embed.set_thumbnail(url=user.display_avatar.url)
    
    if attachment:
        embed.add_field(name="Image Proof:", value="", inline=False)
        embed.set_image(url=attachment.url)
    
    await channeltosend.send(embed=embed)
    await ctx.respond("vouch sent successfully!", ephemeral=True)

    vouch_info = {
        'vouch': message,
        'stars': stars_count,
        'user_name': user.name,
        'vouched_by_id': f"<@!{user.id}>",
        'vouched_by_avatar_url': user.display_avatar.url,
        'vouched_on': current_date,
        'vouch_number': vouch_count,
        'time_stamp': time.isoformat(),
        'attachment': attachment.url if attachment else None
    }
    
    with open(f'vouches/{vouch_count}.json', 'w') as f:
        json.dump(vouch_info, f)

    vouch_count += 1
    save_vouch_count(vouch_count)


@bot.slash_command(name='backupvouches', description='Backup all vouches!', guild_ids=[int(config['guild_id'])])
async def backupvouches(ctx):
    await ctx.defer()
    channeltosend = await bot.fetch_channel(int(config['backup_command_channel']))    
    if not os.listdir('vouches'):
        await ctx.respond("No vouches to backup!", ephemeral=True)
        return
    
    for filename in os.listdir('vouches'):
        try:
            with open(f'vouches/{filename}', 'r') as f:
                vouch = json.load(f)
                stars_display = '⭐' * vouch['stars']

                embed = discord.Embed(title="Backed Up Vouch!", color=embed_color, url=server)
                embed.add_field(name="Vouch:", value=vouch['vouch'], inline=False)
                embed.add_field(name="Stars:", value=stars_display, inline=False)
                embed.add_field(name="Nº:", value=vouch['vouch_number'], inline=True)
                embed.add_field(name="Vouched on:", value=vouch['vouched_on'], inline=True)
                embed.add_field(name="Vouched by:", value=f"{vouch['vouched_by_id']}", inline=True)
                embed.set_thumbnail(url=vouch['vouched_by_avatar_url'])
                embed.set_footer(text=footertext)
                
                if 'time_stamp' in vouch:
                    time_stamp = datetime.fromisoformat(vouch['time_stamp'])  
                    embed.timestamp = time_stamp
                
                if vouch['attachment']:
                    embed.set_image(url=vouch['attachment'])
                
                await channeltosend.send(embed=embed)
                await ctx.respond("backed up vouches successfully", ephemeral=True)
                print(f"Backed up vouch! number: {filename}")
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON file: {filename}")
            continue

clear()
title()
print(Fore.LIGHTMAGENTA_EX + Center.XCenter("""
┌┬┐┬ ┬┬ ┌┬┐┬┌┐ ┌─┐┌─┐┌─┐┌┬┐┌─┐
││││ ││  │ │├┴┐│ ││ │└─┐ │ └─┐
┴ ┴└─┘┴─┘┴ ┴└─┘└─┘└─┘└─┘ ┴ └─┘\n"""))
bot.run(config['bot_token'])
