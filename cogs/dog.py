import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import gc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DOG_API_KEY = os.getenv("DOG_API_KEY")


class Dog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        print("cog_unload triggered (dog)")
        if self.session and not self.session.closed:
            await self.session.close()
            
        gc.collect()

    @app_commands.command(name="dog", description="Fetch a random dog image.")
    async def fetch_dog(self, interaction: discord.Interaction):
        api_url = "https://api.thedogapi.com/v1/images/search"
        headers = {"x-api-key": DOG_API_KEY}

        await interaction.response.defer(thinking=True)
        try:
            async with self.session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    await interaction.followup.send(
                        f"API request failed with status code {response.status}."
                    )
                    return

                data = await response.json()
                if data:
                    image_url = data[0]["url"]
                    await interaction.followup.send(image_url)
                else:
                    await interaction.followup.send("No image found.")
        except aiohttp.ClientError as e:
            await interaction.followup.send(f"An error occurred: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Dog(bot))