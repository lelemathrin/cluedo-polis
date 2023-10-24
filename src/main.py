import discord
from dotenv import load_dotenv
import os
import openai

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = discord.Client(intents=intents)

class Personnage:
    def __init__(self, nom, metier, status, hierarchy):
        self.nom = nom
        self.metier = metier
        self.status = status
        self.hierarchy = hierarchy

    def introduce_hisself(self):
        return f"Bonjour, je m'appelle {self.nom} et je suis le {self.metier}."

    def get_job(self):
        return f"Je suis le {self.metier}."

    def get_name(self):
        return f"Je suis {self.nom}."

channels_to_personnages = {
    "premier": Personnage("Alice", "archéologue", True, False),
    "second": Personnage("Bob", "informaticien", True, False),
    "troisieme": Personnage("Carole", "chimiste", True, False),
    "commissariat": Personnage("David", "détective", True, True)
}

async def chat_with_gpt(message, personnage):
    user_message = message.content
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Jouez un jeu de rôle : Vous êtes {personnage.nom}, un {personnage.metier}. Interagissez comme si vous étiez ce personnage.\nUtilisateur : {user_message}\nIA:",
            max_tokens=150
        )
        response_text = response.choices[0].text
        return response_text
    except Exception as e:
        return str(e)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/parler'):
        await message.channel.send(f'Dans le serveur : {message.guild.name}, avec qui voulez-vous parler : Alice, Bob, Carole ou David ?')

        def check(m):
            return m.author == message.author and m.channel == message.channel

        response = await client.wait_for('message', check=check)

        personnage = None
        for nom, pers in channels_to_personnages.items():
            if nom.lower() in response.content.lower():
                personnage = pers
                break

        if personnage:
            await message.channel.send(personnage.introduce_hisself())
        else:
            await message.channel.send("Personnage non trouvé.")

    if message.content.startswith('/hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('/quoi'):
        await message.channel.send('feur!')

    if message.content.startswith('/play'):
        user = message.author
        guild = message.guild
        category_name = f"game_category_{user.name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True)
        }

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name, overwrites=overwrites)

        channel_names = list(channels_to_personnages.keys())

        for name in channel_names:
            channel = await guild.create_text_channel(name, category=category)
            await channel.send(f'Bienvenue dans {name} !')

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

    if message.channel.name in channels_to_personnages:
        personnage = channels_to_personnages[message.channel.name]

        if personnage.status:
            response_text = await chat_with_gpt(message, personnage)
            await message.channel.send(response_text)

client.run(token)
