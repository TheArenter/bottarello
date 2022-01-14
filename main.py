from telethon import events, TelegramClient
from telethon.tl.custom import Button
from dotenv import load_dotenv
import json
import asyncio
import random
import os

load_dotenv()

bot_token = os.environ['TOKEN']
api_hash = os.environ['API_HASH']
api_id = os.environ['API_ID']
owner = os.environ['OWNER']

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

lastmessage = ""

with open('oggetti.json') as f:
    oggetti = json.load(f)

with open('registered.json') as f:
    registrati = json.load(f)


async def main():
    await bot.start()
    print('Carico e pronto!')
    await bot.run_until_disconnected()


async def start(event):
    global registrati
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    if sender in registrati:
        await bot.send_message(chat, "Guarda un po' chi si rivede 😊")
    else:
        print(sender + ": Ha avviato il bot")
        await bot.send_message(chat, "Ciao bellezza!\nProva ad usare /scheda o /cerca!")
        my_dict = {"Username": sender,
                   "Stop": False,
                   "Userid": uid,
                   "Gender": "Imposta il tuo genere con /sesso",
                   "Age": "Imposta la tua età con /anni",
                   "Inventario": []}
        with open("player/" + str(uid) + '.json', 'w') as file:
            json.dump(my_dict, file)
        coppia = {sender: uid}
        registrati.update(coppia)
        with open('registered.json', 'w') as file:
            json.dump(registrati, file)


@bot.on(events.CallbackQuery(data=b'Maschio'))
@bot.on(events.CallbackQuery(data=b'Femmina'))
async def scsesso(event):
    uid = (await event.get_sender()).id
    if event.data == b'Maschio':
        gender = "Maschio"
    else:
        gender = "Femmina"
    await event.edit('Hai impostato il tuo genere su {}!'.format(gender))
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    my_dict["Gender"] = gender
    with open("player/" + str(uid) + '.json', 'w') as file:
        json.dump(my_dict, file)


async def scheda(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    testo = "La tua scheda:"
    ignora = ['Inventario']
    for the_key, the_value in my_dict.items():
        if the_key not in ignora:
            testo += "\n" + str(the_key) + " : " + str(the_value)
    await bot.send_message(chat, testo)


async def sesso(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    if my_dict['Gender'] == "Imposta il tuo genere con /sesso" or my_dict['Gender'] == "":
        await bot.send_message(chat, 'Sei un Maschio o una Femmina?',
                               buttons=[Button.inline('Maschio', 'Maschio'), Button.inline('Femmina', 'Femmina')])
    else:
        await bot.send_message(chat, 'Hai già impostato il tuo genere su {}'.format(my_dict['Gender']))


async def anni(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    if my_dict['Age'] != "Imposta la tua età con /anni" and my_dict['Age'] != "":
        await bot.send_message(chat, 'Hai già impostato la tua età a {} anni!'.format(my_dict['Age']))
    else:
        async with bot.conversation(chat) as conv:
            await conv.send_message('Quanti anni hai?')
            response = await conv.get_response()
            ann = response.text
            if not ann.isdecimal():
                await bot.send_message(chat, 'L\'età deve essere un numero!')
                await anni(event)
            else:
                await bot.send_message(chat, 'Hai impostato la tua età a {}'.format(ann))
                my_dict["Age"] = ann
                with open("player/" + str(uid) + '.json', 'w') as file:
                    json.dump(my_dict, file)


async def cerca(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    sender = (await event.get_sender()).username
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    att_cerca = my_dict["Stop"]
    if att_cerca:
        await bot.send_message(chat, "Devi aspettare ancora un po'")
    else:
        oggetto = random.choice(oggetti)
        text = sender + " ti guardi un po' intorno ed alla fine in un grosso baule trovi **{}**." \
                        "\nControlla il tuo zaino con /zaino".format(oggetto)
        await bot.send_message(chat, text)
        print(sender + ": " + oggetto)
        my_dict["Inventario"] += [oggetto]
        my_dict["Stop"] = not att_cerca
        with open("player/" + str(uid) + '.json', 'w') as file:
            json.dump(my_dict, file)
        await aspettacerca(uid)


async def aspettacerca(uid):
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    att_cerca = my_dict["Stop"]
    await asyncio.sleep(30)
    my_dict["Stop"] = not att_cerca
    with open("player/" + str(uid) + '.json', 'w') as file:
        json.dump(my_dict, file)
    await bot.send_message(uid, "Puoi tornare a cercare!")


async def zaino(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    inventario = my_dict["Inventario"]
    tot = len(set(inventario))
    sacca = "Possiedi (" + str(tot) + "):\n"
    for x in inventario:
        if x not in sacca:
            sacca += x + " x " + str(inventario.count(x)) + "\n"
    await bot.send_message(chat, sacca)


async def additem(event):
    global oggetti
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    if sender not in owner:
        await bot.send_message(chat, "Non puoi usare questo comando!")
    else:
        parts = event.raw_text.split(" ", 1)
        if len(parts) <= 1:
            await bot.send_message(chat, "Non hai specificato l'ggetto!")
        else:
            arg = parts[1]
            oggetti.append(arg)
            with open('oggetti.json', 'w') as file:
                json.dump(oggetti, file)
            await bot.send_message(chat, "Ho aggiunto {} all'elenco!".format(arg))
            print(oggetti)


async def cercaoggetto(event):
    global oggetti
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    inventario = my_dict["Inventario"]
    parts = event.raw_text.split(" ", 1)
    if len(parts) <= 1:
        await bot.send_message(chat, "Oggetto non specificato!")
    else:
        arg = parts[1].lower()
        if len(arg) < 3:
            await bot.send_message(chat, "Mi servono almeno 3 lettere per cercare un oggetto!")
        else:
            matches = [match for match in inventario if arg in match.lower()]
            if not matches:
                await bot.send_message(chat, "Non possiedi questo oggetto!")
            else:
                text = "Ho trovato:\n"
                for match in matches:
                    if match not in text:
                        num = matches.count(match)
                        text += str(match) + " x " + str(num) + "\n"
                await bot.send_message(chat, text)


async def daioggetto(event):
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    parts = event.raw_text.split(" ", 2)
    if len(parts) < 2:
        await bot.send_message(chat, "Per dare un oggeto usa /dai <Giocaotre> <Oggetto>")
    else:
        cont = parts[1].lower()
        gift = parts[2].lower()
        cercaplayer = [match for match in registrati if cont in match.lower()]
        if not cercaplayer:
            await bot.send_message(chat, "Non ho trovato questo giocatore!")
        else:
            with open("player/" + str(uid) + '.json') as file:
                my_dict = json.load(file)
            inventario = my_dict["Inventario"]
            cercagift = [matchx for matchx in inventario if gift in matchx.lower()]
            if not cercagift:
                await bot.send_message(chat, "Non possiedi questo oggetto!")
            else:
                pr_gift = cercagift[0]
                pr_player = cercaplayer[0]
                idricevente = registrati[pr_player]
                with open("player/" + str(uid) + '.json') as filex:
                    my_dict = json.load(filex)
                my_dict["Inventario"].remove(pr_gift)
                with open("player/" + str(uid) + '.json', 'w') as filex:
                    json.dump(my_dict, filex)
                await bot.send_message(uid, "Hai dato {} a {}!".format(pr_gift, pr_player))
                with open("player/" + str(idricevente) + '.json') as filey:
                    my_dict = json.load(filey)
                my_dict["Inventario"].append(pr_gift)
                with open("player/" + str(idricevente) + '.json', 'w') as filey:
                    json.dump(my_dict, filey)
                await bot.send_message(idricevente, "{} ti ha dato {}!".format(sender, pr_gift))
                print(sender + " ha dato " + pr_gift + " a " + pr_player)


@bot.on(events.NewMessage(pattern=r'(?i).*heck'))
async def handler(event):
    await event.delete()
    sender = await event.get_sender()
    print("Deleted: " + event.raw_text + " sent by " + sender.username + " " + str(event.sender_id))


with bot:
    @bot.on(events.NewMessage)
    async def handler(event):
        #  global lastmessage
        #  lastmessage = event.raw_text
        if '/start' in event.raw_text:
            await start(event)
        elif '/sesso' in event.raw_text:
            await sesso(event)
        elif '/scheda' in event.raw_text:
            await scheda(event)
        elif '/anni' in event.raw_text:
            await anni(event)
        elif '/cerca' in event.raw_text:
            await cerca(event)
        elif '/zaino' in event.raw_text:
            await zaino(event)
        elif 'hello' in event.raw_text:
            await event.reply('hi!')
        elif '/additem' in event.raw_text:
            await additem(event)
        elif '/oggetto' in event.raw_text:
            await cercaoggetto(event)
        elif '/dai' in event.raw_text:
            await daioggetto(event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())