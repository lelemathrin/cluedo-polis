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

# Créer une liste des armes
armes = [
    "Le Poison Spectral",
    "La Dague des Ténèbres",
    "Le Sceptre Ensorcelé",
    "Le Masque Maudit",
    "La Fiole d'Éclairs Fantômes",
    "Le Livre des Malédictions"
]

suspects = [
    "Archibald Obscurus", 
    "Scarlett Sombreval", 
    "Orion Sangfroid", 
    "Casyope Lycanthrope", 
    "Edgar Frisson"
]

arme_choisie = ""
tueur = ""

class Personnage:
    def __init__(self, nom, metier, alibi, status, hierarchy, image_path, description):
        self.nom = nom
        self.metier = metier
        self.alibi = alibi
        self.status = status
        self.hierarchy = hierarchy
        self.image_path = image_path
        self.description = description  # Nouvelle propriété pour la description

    def introduce_himself(self):
        return f"Bonjour, je m'appelle {self.nom} et je suis le {self.metier}."

    def get_job(self):
        return f"Je suis le {self.metier}."

    def get_name(self):
        return f"Je suis {self.nom}."

channels_to_personnages = {
    "commissariat": Personnage("David", "détective", "Tu es le commissaire, tu n'as donc pas d'alibi.", True, True, "assets/commissariat.webp", ""),
    "archibald_obscurus": Personnage("Monsieur Archibald Obscurus", "fantôme, boulanger", "Il prétendait être dans sa cuisine en train de préparer la soirée d'Halloween, vérifiable par des notes et des préparatifs retrouvés.", True, False, "assets/archibald_obscurus.webp", "Un érudit calme et énigmatique, obsédé par l'étude des phénomènes surnaturels. Il parle rarement de lui-même, préférant discuter de sujets ésotériques avec ceux qui peuvent le suivre dans ses intérêts."),
    "scarlett_sombreval": Personnage("Mademoiselle Scarlett Sombreval", "sorcière, infirmière", "Elle prétendait être dans le Jardin des  mes Perdues, prenant l'air entre les préparatifs de la fête. Certains invités peuvent confirmer avoir vu une silhouette féminine dans l'obscurité.", True, False, "assets/scarlett_sombreval.webp", "Une actrice théâtrale charismatique avec une passion pour le macabre. Elle est extravertie, aime être au centre de l'attention et a une collection de souvenirs de films d'horreur dans sa chambre."),
    "orion_sangfroid": Personnage("Orion Sangfroid", "diable, fleuriste", "il affirmait être dans le Salon des Ombres Éternelles, admirant la collection d'armes. Des invités ont peut-être croisé son chemin pendant cette période.", True, False, "assets/orion_sangfroid.webp", "Un homme stoïque avec une fascination pour les fleurs. Il parle peu de ses propres expériences, mais son regard intense suggère une vie pleine de mystères."),
    "casyope_lycanthrope": Personnage("Casyope Lycanthrope", "loup-garou maire fan de science", "Il prétendait être dans son Laboratoire Interdit, travaillant sur des expériences. Des résidus ou des indices de son travail pourraient être trouvés dans le laboratoire.", True, False, "assets/casyope_lycanthrope.webp", "Un maire et scientifique déterminé et curieux, passionné par l'étude des créatures surnaturelles. Il est pragmatique et sceptique, mais toujours ouvert à la découverte de nouvelles vérités."),
    "edgar_frisson": Personnage("Monsieur Edgar Frisson", "zombie, facteur", " Il prétendait être dans la salle à manger, supervisant les préparatifs du dîner. Des témoignages d'autres membres du personnel pourraient confirmer ou réfuter cette affirmation.", True, False, "assets/edgar_frisson.webp", "Il est discret, mais il semble avoir un sixième sens pour les mystères. Sa présence discrète cache peut-être plus qu'il ne le laisse paraître.")
}

user_message_count = {}  # Format : {user_id: {channel_name: count}}
user_questions_history = {}  # {user_id: {channel_name: ["question1", "question2", ...]}}

async def chat_with_gpt(message, personnage, previous_questions):
    user_message = message.content
    additional_info = "L'utilisateur a le droit à seulement cinq questions par jour."
    if personnage.nom == "David":  # Si le personnage est le commissaire David
        additional_info = "L'utilisateur doit interroger les autres personnages et trouvez qui a causé la mort de Madame DeLune et avec quelle arme. Pour accomplir ça, l'utilisateur à le droit à une seule proposition par jour pour déterminer qui est le tueur et quelle est son arme."  
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Tu joues à un jeu de rôle dans le style de cluedo : Tu es {personnage.nom}, un {personnage.metier}, {personnage.description}. Ton alibi est : {personnage.alibi}. Tu dois intéragir UNIQUEMENT comme si tu étais ce personnage, avec l'utilisateur qui va essayer de devenir qui est le tueur. {additional_info}. Voici l'histoire du jeu : L'histoire commence lors d'une nuit sombre et pluvieuse, alors que les six invités se retrouvent au Manoir des Ombres pour une soirée d'Halloween inoubliable. Soudain, un éclair déchire le ciel, plongeant la demeure dans l'obscurité. Lorsque la lumière revient, Madame Mortisia DeLune est retrouvée morte dans le hall, son corps entouré de bougies vacillantes. Chacun des personnages cache un sombre secret, et ils sont tous suspects. Pour cette partie, le tueur sera {tueur} et l'arme du meurtre sera {arme_choisie}. L'historique des questions : {previous_questions} \nUtilisateur : {user_message}\nIA:",
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
    global tueur
    if message.author == client.user:
        return

    if message.content.startswith('/hello'):    
        await message.channel.send('Hello!')
    if message.content.startswith('/quoi'):
        await message.channel.send('feur!')
        
    # Limiter la longueur des messages dans les canaux créés
    if message.channel.category and message.channel.category.name.startswith("game_category_"):
        if len(message.content) > 150:
            await message.channel.send("**Votre message est trop long ! Il ne doit pas dépasser 150 caractères.**")
            return  # Ne pas traiter ce message plus loin et ne pas mettre à jour le compteur

    if message.channel.name == "commissariat":
        user = message.author

        if tueur in message.content:
            await message.channel.send(f'Félicitations, {user.mention} a trouvé le coupable ({tueur}) !')
            
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
        loading = (
            "Création des channels des personnages..."
        )
        await message.channel.send(loading)
        
        # Choisir un tueur aléatoirement parmi les suspects
        tueur = random.choice(suspects)
        print(tueur)
        
        # Choisir une arme aléatoirement
        arme_choisie = random.choice(armes)
        print(arme_choisie)
        
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
        await commissaire_channel.send(f'**Bienvenue dans le canal du commissariat !**\n\n**Métier:** {channels_to_personnages["commissariat"].metier}\n')
        await commissaire_channel.send(file=discord.File(channels_to_personnages["commissariat"].image_path))

        other_character_names = ["Archibald Obscurus", "Scarlett Sombreval", "Orion Sangfroid", "Casyope Lycanthrope", "Edgar Frisson"]
        random.shuffle(other_character_names)

        for name in other_character_names[:6]:  
            channel_name = name.replace(" ", "_").lower()
            channel = await guild.create_text_channel(channel_name, category=category)
            personnage = channels_to_personnages[channel_name]

            if personnage.description:
                await channel.send(f'**Bienvenue dans le canal de {personnage.nom} !**\n\n**Métier:** {personnage.metier}\n\n**Description:** {personnage.description}\n')
                await channel.send(file=discord.File(personnage.image_path))
            else:
                await channel.send(f'**Bienvenue dans le canal de {personnage.nom} !**\n\n**Métier:** {personnage.metier}\n')
                await channel.send(file=discord.File(personnage.image_path))

        general_channel = discord.utils.get(guild.text_channels, name="général")
        if general_channel:
            presentation_message = (
                "\n"
                ":mag: Bienvenue dans **NeoMystère**, un jeu de mystère interactif!\n"
                ":house: Vous vous trouvez dans un manoir mystérieux avec plusieurs canaux, chacun contenant un personnage différent.\n"
                ":question: Votre mission est de poser des questions aux personnages pour en savoir plus sur eux.\n"
                ":police_officer::skin-tone-2: À la fin de votre enquête, vous pourrez donner votre verdict au commissariat pour tenter de résoudre le mystère.\n"
                ":calendar: Vous avez droit à 5 questions/personnage par jour et une réponse au commissariat par jour. Le jeu dure une semaine."
            )
            await general_channel.send(presentation_message)
            await general_channel.send(file=discord.File("assets/manoir.jpg"))
            



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
        
        user_id = message.author.id
        channel_name = message.channel.name
        
        # Mise à jour de l'historique
        if user_id not in user_questions_history:
            user_questions_history[user_id] = {}
        if channel_name not in user_questions_history[user_id]:
            user_questions_history[user_id][channel_name] = []
        user_questions_history[user_id][channel_name].append(message.content)

        # Vérifier le compteur de messages
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
            previous_questions = "\n".join(user_questions_history[user_id][channel_name])
            response_text = await chat_with_gpt(message, personnage, previous_questions)  # Passez l'historique comme argument supplémentaire
            formatted_response = f"**{personnage.nom}**: {response_text}"
            await message.channel.send(formatted_response)

client.run(token)