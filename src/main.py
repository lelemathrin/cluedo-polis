import discord
from dotenv import load_dotenv
import os
import openai
import random

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = discord.Client(intents=intents)

class Personnage:
    def __init__(self, nom, metier, status, hierarchy, description):
        self.nom = nom
        self.metier = metier
        self.status = status
        self.hierarchy = hierarchy
        self.description = description  # Nouvelle propriété pour la description

    def introduce_hisself(self):
        return f"Bonjour, je m'appelle {self.nom} et je suis le {self.metier}."

    def get_job(self):
        return f"Je suis le {self.metier}."

    def get_name(self):
        return f"Je suis {self.nom}."

channels_to_personnages = {
    "commissariat": Personnage("David", "détective", True, True, ""),
    "Archibald Obscurus": Personnage("Monsieur Archibald Obscurus", "fantôme, boulanger", True, False, "Un érudit calme et énigmatique, obsédé par l'étude des phénomènes surnaturels. Il parle rarement de lui-même, préférant discuter de sujets ésotériques avec ceux qui peuvent le suivre dans ses intérêts."),
    "Scarlett Sombreval": Personnage("Mademoiselle Scarlett Sombreval", "sorcière, infirmière", True, False, "Une actrice théâtrale charismatique avec une passion pour le macabre. Elle est extravertie, aime être au centre de l'attention et a une collection de souvenirs de films d'horreur dans sa chambre."),
    "Orion Sangfroid": Personnage("Orion Sangfroid", "diable, fleuriste", True, False, "Un homme stoïque avec une fascination pour les fleurs. Il parle peu de ses propres expériences, mais son regard intense suggère une vie pleine de mystères."),
    "Casyope Lycanthrope": Personnage("Casyope Lycanthrope", "loup-garou maire fan de science", True, False, "Un maire et scientifique déterminé et curieux, passionné par l'étude des créatures surnaturelles. Il est pragmatique et sceptique, mais toujours ouvert à la découverte de nouvelles vérités."),
    "Edgar Frisson": Personnage("Monsieur Edgar Frisson", "zombie, facteur", True, False, "Il est discret, mais il semble avoir un sixième sens pour les mystères. Sa présence discrète cache peut-être plus qu'il ne le laisse paraître.")
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

        # Le commissaire a toujours son propre canal
        commissaire_channel = await guild.create_text_channel("commissariat", category=category)
        await commissaire_channel.send(f'Bienvenue dans le canal du commissariat !\nMétier: {channels_to_personnages["commissariat"].metier}')

        # Les noms des autres personnages
        other_character_names = ["Archibald Obscurus", "Scarlett Sombreval", "Orion Sangfroid", "Casyope Lycanthrope", "Edgar Frisson"]
        random.shuffle(other_character_names)  # Mélange les noms aléatoirement

        # Crée un canal pour chaque personnage
        for name in other_character_names[:6]:  
            channel_name = name.replace(" ", "_").lower()
            channel = await guild.create_text_channel(channel_name, category=category)
            personnage = channels_to_personnages[name]
            
            # Si le personnage a une description, envoyez-la.
            if personnage.description:
                await channel.send(f'Bienvenue dans le canal de {personnage.nom} !\nMétier: {personnage.metier}\nDescription: {personnage.description}')
            else:
                await channel.send(f'Bienvenue dans le canal de {personnage.nom} !\nMétier: {personnage.metier}')


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
