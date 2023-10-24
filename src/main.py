import discord

token = 'MTE2NjAwNjY4NTcxNDg4MjYxMQ.G9CAk3.B18Qi0pGPGWyu55_g8_O84qQ2VPJnWWvOBOFVg'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Définissez la classe Personnage ici
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
        await message.channel.send(f'Dans le canal : {message.channel.name}, avec qui voulez-vous parler : Alice ou Bob ?')

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
        # Créer les canaux "premier," "second," et "troisieme" dans le salon "game"
        guild = message.guild
        category_name = "game"  # Nom du salon de catégorie

        # Vérifiez si la catégorie "game" existe, sinon, créez-la
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        channel_names = ["premier", "second", "troisieme"]

        for name in channel_names:
            await guild.create_text_channel(name, category=category)

        await message.channel.send('Canaux créés : premier, second, troisieme dans le salon "game"')

    if message.content.startswith('/end'):
        # Supprimer les canaux "premier," "second," et "troisieme" dans la catégorie "game"
        guild = message.guild
        category_name = "game"  # Nom du salon de catégorie

        category = discord.utils.get(guild.categories, name=category_name)
        if category:
            channel_names = ["premier", "second", "troisieme"]

            for name in channel_names:
                channel = discord.utils.get(category.text_channels, name=name)
                if channel:
                    await channel.delete()

            # Supprimer la catégorie "game"
            await category.delete()

        await message.channel.send('Canaux supprimés : premier, second, troisieme et la catégorie "game"')

    if message.content.startswith('/'):
        # Afficher les commandes disponibles
        available_commands = [
            "",
            "\t/parler : Pour discuter avec Alice ou Bob.",
            "\t/hello : Pour dire bonjour.",
            "\t/start : Pour créer les canaux de jeu.",
            "\t/end : Pour supprimer les canaux de jeu et la catégorie."
        ]

        response = "\n".join(available_commands)
        await message.channel.send(f'Commandes disponibles :\n{response}')

client.run(token)
