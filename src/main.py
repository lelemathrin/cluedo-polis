import discord
from dotenv import load_dotenv
import os
import openai
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = discord.Client(intents=intents)

class Personnage:
    def __init__(self, nom, metier, status, hierarchy, image_path, description):
        self.nom = nom
        self.metier = metier
        self.status = status
        self.hierarchy = hierarchy
        self.image_path = image_path
        self.description = description  # Nouvelle propriété pour la description

    def introduce_hisself(self):
        return f"Bonjour, je m'appelle {self.nom} et je suis le {self.metier}."

    def get_job(self):
        return f"Je suis le {self.metier}."

    def get_name(self):
        return f"Je suis {self.nom}."

channels_to_personnages = {
    "commissariat": Personnage("David", "détective", True, True, "assets/11minutos.jpg", ""),
    "archibald_obscurus": Personnage("Monsieur Archibald Obscurus", "fantôme, boulanger", True, False, "assets/11minutos.jpg", "Un érudit calme et énigmatique, obsédé par l'étude des phénomènes surnaturels. Il parle rarement de lui-même, préférant discuter de sujets ésotériques avec ceux qui peuvent le suivre dans ses intérêts."),
    "scarlett_sombreval": Personnage("Mademoiselle Scarlett Sombreval", "sorcière, infirmière", True, False, "assets/11minutos.jpg", "Une actrice théâtrale charismatique avec une passion pour le macabre. Elle est extravertie, aime être au centre de l'attention et a une collection de souvenirs de films d'horreur dans sa chambre."),
    "orion_sangfroid": Personnage("Orion Sangfroid", "diable, fleuriste", True, False, "assets/11minutos.jpg", "Un homme stoïque avec une fascination pour les fleurs. Il parle peu de ses propres expériences, mais son regard intense suggère une vie pleine de mystères."),
    "casyope_lycanthrope": Personnage("Casyope Lycanthrope", "loup-garou maire fan de science", True, False, "assets/lhommeleplusaigridefrance.jpg", "Un maire et scientifique déterminé et curieux, passionné par l'étude des créatures surnaturelles. Il est pragmatique et sceptique, mais toujours ouvert à la découverte de nouvelles vérités."),
    "edgar_frisson": Personnage("Monsieur Edgar Frisson", "zombie, facteur", True, False, "assets/lhommeleplusaigridefrance.jpg", "Il est discret, mais il semble avoir un sixième sens pour les mystères. Sa présence discrète cache peut-être plus qu'il ne le laisse paraître.")
}

user_message_count = {}  # Format : {user_id: {channel_name: count}}

async def chat_with_gpt(message, personnage):
    user_message = message.content
    additional_info = "L'utilisateur a le droit à seulement cinq questions par jour."
    if personnage.nom == "David":  # Si le personnage est le commissaire David
        additional_info = "L'utilisateur a le droit à une seule proposition par jour pour déterminer qui est le tueur."
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Tu joues à un jeu de rôle dans le style de cluedo : Tu es {personnage.nom}, un {personnage.metier}, {personnage.description}. Tu dois intéragir UNIQUEMENT comme si tu étais ce personnage, avec l'utilisateur qui va essayer de devenir qui est le tueur. {additional_info}. Voici l'histoire du jeu : L'histoire commence lors d'une nuit sombre et pluvieuse, alors que les six invités se retrouvent au Manoir des Ombres pour une soirée d'Halloween inoubliable. Soudain, un éclair déchire le ciel, plongeant la demeure dans l'obscurité. Lorsque la lumière revient, Madame Mortisia DeLune est retrouvée morte dans le hall, son corps entouré de bougies vacillantes. Chacun des personnages cache un sombre secret, et ils sont tous suspects. Les invités doivent fouiller le manoir pour trouver des indices, interroger les autres personnages et résoudre le mystère de la mort de Madame DeLune. \nUtilisateur : {user_message}\nIA:",
            max_tokens=150
        )
        response_text = response.choices[0].text
        return response_text
    except Exception as e:
        return str(e)

async def reset_daily_counts():
    while True:
        await asyncio.sleep(86400)
        user_message_count.clear()
        
@client.event
async def on_ready():
    client.loop.create_task(reset_daily_counts())
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('/quoi'):
        await message.channel.send('feur!')

    if message.channel.name == "commissariat":
        user = message.author
        suspect_name = "NomDuSuspect"

        if suspect_name in message.content:
            await message.channel.send(f'Félicitations, {user.mention} a trouvé le coupable ({suspect_name}) !')
            
            await asyncio.sleep(5)
            user = message.author
            guild = message.guild
            category_name = f"game_category_{user.name}"

            category = discord.utils.get(guild.categories, name=category_name)
            if category:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()

            await message.channel.send(f'Canaux et catégorie supprimés pour l\'utilisateur {user.name}')
            
            
            

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

        commissaire_channel = await guild.create_text_channel("commissariat", category=category)
        await commissaire_channel.send(f'Bienvenue dans le canal du commissariat !\nMétier: {channels_to_personnages["commissariat"].metier}')
        await commissaire_channel.send(file=discord.File(channels_to_personnages["commissariat"].image_path))

        other_character_names = ["Archibald Obscurus", "Scarlett Sombreval", "Orion Sangfroid", "Casyope Lycanthrope", "Edgar Frisson"]
        random.shuffle(other_character_names)

        for name in other_character_names[:6]:  
            channel_name = name.replace(" ", "_").lower()
            channel = await guild.create_text_channel(channel_name, category=category)
            personnage = channels_to_personnages[channel_name]

            if personnage.description:
                await channel.send(f'Bienvenue dans le canal de {personnage.nom} !\nMétier: {personnage.metier}\nDescription: {personnage.description}')
                await channel.send(file=discord.File(personnage.image_path))
            else:
                await channel.send(f'Bienvenue dans le canal de {personnage.nom} !\nMétier: {personnage.metier}')
                await channel.send(file=discord.File(personnage.image_path))

        general_channel = discord.utils.get(guild.text_channels, name="général")
        if general_channel:
            presentation_message = (
                "\n"
                ":mag: Bienvenue dans NeoMystère, un jeu de mystère interactif!\n"
                ":house: Vous vous trouvez dans un manoir mystérieux avec plusieurs canaux, chacun contenant un personnage différent.\n"
                ":question: Votre mission est de poser des questions aux personnages pour en savoir plus sur eux.\n"
                ":police_officer::skin-tone-2: À la fin de votre enquête, vous pourrez donner votre verdict au commissariat pour tenter de résoudre le mystère.\n"
                ":calendar: Vous avez droit à 5 questions/personnage par jour et une réponse au commissariat par jour. Le jeu dure une semaine."
            )
            await general_channel.send(presentation_message)



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
        
        # Vérifier la limite de messages
        user_id = message.author.id
        channel_name = message.channel.name
        if user_id not in user_message_count:
            user_message_count[user_id] = {}
        if channel_name not in user_message_count[user_id]:
            user_message_count[user_id][channel_name] = 0

        # Définir la limite en fonction du canal
        limit = 1 if channel_name == "commissariat" else 5

        if user_message_count[user_id][channel_name] >= limit:
            await message.channel.send("Désolé, vous avez atteint votre limite de messages pour aujourd'hui pour ce personnage.")
            return  # Ne pas répondre

        # Si la limite n'est pas atteinte, augmenter le compteur et continuer
        user_message_count[user_id][channel_name] += 1

        if personnage.status:
            response_text = await chat_with_gpt(message, personnage)
            formatted_response = f"**{personnage.nom}**: {response_text}"
            await message.channel.send(formatted_response)


client.run(token)