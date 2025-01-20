import os
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Check if the token is available
if not TOKEN:
    raise ValueError("Bot token is missing. Ensure it's in the .env file.")

# Set up bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# URL list for tracking spawns
URLS = {
    "Cell": "https://psycord.com/pokedex?poke=zygarde+%28cell%29",
    "Core": "https://psycord.com/pokedex?poke=zygarde+%28core%29",
    "Spinda": "https://psycord.com/pokedex?poke=spinda",
    "Lapras": "https://psycord.com/pokedex?poke=lapras",
    "Smeargle": "https://psycord.com/pokedex?poke=smeargle",
    "Varoom": "https://psycord.com/pokedex?poke=varoom",
    "Unown A": "https://psycord.com/pokedex?poke=unown+%28a%29",
    "Unown B": "https://psycord.com/pokedex?poke=unown+%28b%29",
    "Unown C": "https://psycord.com/pokedex?poke=unown+%28c%29",
    "Unown D": "https://psycord.com/pokedex?poke=unown+%28d%29",
    "Unown E": "https://psycord.com/pokedex?poke=unown+%28e%29",
    "Unown F": "https://psycord.com/pokedex?poke=unown+%28f%29",
    "Unown G": "https://psycord.com/pokedex?poke=unown+%28g%29",
    "Unown H": "https://psycord.com/pokedex?poke=unown+%28h%29",
    "Unown I": "https://psycord.com/pokedex?poke=unown+%28i%29",
    "Unown J": "https://psycord.com/pokedex?poke=unown+%28j%29",
    "Unown K": "https://psycord.com/pokedex?poke=unown+%28k%29",
    "Unown L": "https://psycord.com/pokedex?poke=unown+%28l%29",
    "Unown M": "https://psycord.com/pokedex?poke=unown+%28m%29",
    "Unown N": "https://psycord.com/pokedex?poke=unown+%28n%29",
    "Unown O": "https://psycord.com/pokedex?poke=unown+%28o%29",
    "Unown P": "https://psycord.com/pokedex?poke=unown+%28p%29",
    "Unown Q": "https://psycord.com/pokedex?poke=unown+%28q%29",
    "Unown R": "https://psycord.com/pokedex?poke=unown+%28r%29",
    "Unown S": "https://psycord.com/pokedex?poke=unown+%28s%29",
    "Unown T": "https://psycord.com/pokedex?poke=unown+%28t%29",
    "Unown U": "https://psycord.com/pokedex?poke=unown+%28u%29",
    "Unown V": "https://psycord.com/pokedex?poke=unown+%28v%29",
    "Unown W": "https://psycord.com/pokedex?poke=unown+%28w%29",
    "Unown X": "https://psycord.com/pokedex?poke=unown+%28x%29",
    "Unown Y": "https://psycord.com/pokedex?poke=unown+%28y%29",
    "Unown Z": "https://psycord.com/pokedex?poke=unown+%28z%29",
    "Raikou": "https://psycord.com/pokedex?poke=Raikou",
    "Entei": "https://psycord.com/pokedex?poke=Entei",
    "Suicune": "https://psycord.com/pokedex?poke=Suicune",
    "Zygarde": "https://psycord.com/pokedex?poke=zygarde",
    "Zacian": "https://psycord.com/pokedex?poke=zacian",
    "Zamazenta": "https://psycord.com/pokedex?poke=zamazenta",
    "Latias": "https://psycord.com/pokedex?poke=latias",
    "Latios": "https://psycord.com/pokedex?poke=latios",
    "Spectrier": "https://psycord.com/pokedex?poke=spectrier",
    "Glastrier": "https://psycord.com/pokedex?poke=glastrier",
    "Virizion": "https://psycord.com/pokedex?poke=virizion",
    "Terrakion": "https://psycord.com/pokedex?poke=terrakion",
    "Cobalion": "https://psycord.com/pokedex?poke=cobalion",
}

# Store last spawn locations
last_spawn_locations = {url_name: None for url_name in URLS}

# Function to fetch spawn location from the page
def fetch_spawn_location(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the <li> element by its class
        spawn_li = soup.find('li', class_="list-group-item bg-transparent text-white")

        if spawn_li:
            spawn_text = spawn_li.get_text(strip=True)  # Extract and clean the text
            if spawn_text == "Currently unobtainable.":
                return None  # Treat "Currently unobtainable." as no spawn
            return spawn_text
        else:
            return None  # Return None if the spawn location is not found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the web page: {e}")
        return None

# Task to monitor changes for each URL
@tasks.loop(minutes=2)  # Adjust the interval as needed
async def monitor_spawn_location():
    global last_spawn_locations

    # Loop through all URLs and check for changes
    for url_name, url in URLS.items():
        new_spawn_location = fetch_spawn_location(url)

        if new_spawn_location:  # Only process if we got a valid spawn location
            if new_spawn_location != last_spawn_locations[url_name]:
                # Notify all servers with a "roaming" channel
                for guild in bot.guilds:
                    channel = discord.utils.get(guild.text_channels, name="roaming")
                    if channel:
                        await channel.send(f"Spawn location for {url_name} has changed!\nNew Location: {new_spawn_location}")

                # Update the last known spawn location for the specific URL
                last_spawn_locations[url_name] = new_spawn_location

# Command to manually check the current spawn location
@bot.command()
async def check_spawn(ctx, url_name: str):
    if url_name in URLS:
        spawn_location = fetch_spawn_location(URLS[url_name])
        if spawn_location:
            await ctx.send(f"{url_name}:\n{spawn_location}")
        else:
            await ctx.send(f"Could not find the spawn location for {url_name}.")
    else:
        await ctx.send("Invalid URL name. Please check the available URLs.")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    monitor_spawn_location.start()  # Start the monitoring task

# Run the bot
bot.run(TOKEN)
