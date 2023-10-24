import discord
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=intents)

class Personnage:
    def __init__(self, nom, metier):
        self.nom = nom
        self.metier = metier

    def se_presenter(self):
        return f"Je m'appelle {self.nom} et je suis un {self.metier}."

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/parler'):
        await message.channel.send(f'Dans le serveur : {message.guild.name}, avec qui voulez-vous parler : Alice ou Bob ?')

        def check(m):
            return m.author == message.author and m.channel == message.channel

        response = await client.wait_for('message', check=check)

        if 'Alice' in response.content:
            personnage1 = Personnage("Alice", "archéologue")
            await message.channel.send(personnage1.se_presenter())
        elif 'Bob' in response.content:
            personnage2 = Personnage("Bob", "informaticien")
            await message.channel.send(personnage2.se_presenter())

    if message.content.startswith('/hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('/start'):
        user = message.author
        guild = message.guild
        category_name = f"game_category_{user.name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Les autres ne peuvent pas voir la catégorie
            user: discord.PermissionOverwrite(read_messages=True)  # L'utilisateur peut voir la catégorie
        }

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name, overwrites=overwrites)

        channel_names = ["premier", "second", "troisieme"]

        for name in channel_names:
            await guild.create_text_channel(name, category=category)

        await message.channel.send(f'Canaux créés dans la catégorie "{category_name}"')

    if message.content.startswith('/end'):
        user = message.author
        guild = message.guild
        category_name = f"game_category_{user.name}"

        category = discord.utils.get(guild.categories, name=category_name)
        if category:
            for channel in category.channels:
                await channel.delete()
            await category.delete()

        await message.channel.send(f'Canaux et catégorie supprimés pour l\'utilisateur {user.name}')

client.run(token)
