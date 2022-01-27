from telethon import events, TelegramClient
from telethon.tl.custom import Button
from dotenv import load_dotenv
from random import randint
from datetime import datetime
import liste
import json
import asyncio
import random
import os

load_dotenv()

bot_token = os.environ['TOKEN']
api_hash = os.environ['API_HASH']
api_id = os.environ['API_ID']
owner = os.environ['OWNER']

bot = TelegramClient('bot', int(api_id), api_hash).start(bot_token=bot_token)

lastmessage = ""

with open('oggetti.json') as f:
    oggetti = json.load(f)

with open('registered.json') as f:
    registrati = json.load(f)

infermeria = []
sonno = []
cursed = []
ladro = []
refurtiva = []
rapina = False

usabili = liste.usabili
bullets = liste.bullets
raritylist = liste.raritylist


async def nowtime():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


async def main():
    await bot.start()
    print('Carico e pronto!')
    await bot.run_until_disconnected()


async def opendict(uid):
    with open("player/" + str(uid) + '.json') as file:
        my_dict = json.load(file)
    return my_dict


async def writedict(uid, my_dict):
    with open("player/" + str(uid) + '.json', 'w') as filesta:
        json.dump(my_dict, filesta)


async def start(event):
    dt_string = await nowtime()
    global registrati
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    sender = (await event.get_sender()).username
    if sender:
        if sender in registrati:
            await bot.send_message(chat, "Guarda un po' chi si rivede 😊")
        else:
            print(dt_string, sender + ": Ha avviato il bot")
            await bot.send_message(chat, "Ciao bellezza!\nProva ad usare /scheda o /cerca!")
            my_dict = {"Username": sender,
                       "Stop": False,
                       "Lancio": False,
                       "HP": "50",
                       "Userid": uid,
                       "Gender": "Imposta il tuo genere con /sesso",
                       "Age": "Imposta la tua età con /anni",
                       "Inventario": []}
            await writedict(uid, my_dict)
            coppia = {sender: uid}
            registrati.update(coppia)
            with open('registered.json', 'w') as filesta:
                json.dump(registrati, filesta)
            with open('registered.json') as filesta:
                registrati = json.load(filesta)
    else:
        await bot.send_message(chat, "Ciao, per usare il bot imposta prima un username e poi riprova.")


@bot.on(events.CallbackQuery(data=b'Maschio'))
@bot.on(events.CallbackQuery(data=b'Femmina'))
async def scsesso(event):
    uid = (await event.get_sender()).id
    if event.data == b'Maschio':
        gender = "Maschio"
    else:
        gender = "Femmina"
    await event.edit('Hai impostato il tuo genere su {}!'.format(gender))
    my_dict = await opendict(uid)
    my_dict["Gender"] = gender
    await writedict(uid, my_dict)


@bot.on(events.CallbackQuery(data=b'indaga'))
async def scindaga(event):
    dt_string = await nowtime()
    global rapina
    global ladro
    prob = randint(1, 10)
    if prob <= 5:
        print(dt_string, "Safe...")
        await event.edit('Purtroppo gli indizi non ti hanno portato a nulla!')
        ladro = []
        rapina = False
        print(rapina)
    else:
        print(dt_string, "Caught...")
        idladro = registrati[ladro]
        my_dict = await opendict(idladro)
        ladrohp = my_dict["HP"]
        my_dict["HP"] = ladrohp - 10
        await writedict(idladro, my_dict)
        await event.edit('Le tracce ti hanno portato fino a {}, il tuo oggetto è perso,'
                         ' ma gli hai dato una bella lezione!'.format(ladro))
        await bot.send_message(idladro, 'Sei stato scoperto! Ti hanno dato una bella lezione ed hai perso 10 HP!')
        rapina = False
        await controllohp(ladro, event)
        ladro = []


async def scheda(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    my_dict = await opendict(uid)
    testo = "La tua scheda:"
    ignora = ['Inventario']
    for the_key, the_value in my_dict.items():
        if the_key not in ignora:
            testo += "\n" + str(the_key) + " : " + str(the_value)
    await bot.send_message(chat, testo)


async def sesso(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    my_dict = await opendict(uid)
    if my_dict['Gender'] == "Imposta il tuo genere con /sesso" or my_dict['Gender'] == "":
        await bot.send_message(chat, 'Sei un Maschio o una Femmina?',
                               buttons=[Button.inline('Maschio', 'Maschio'), Button.inline('Femmina', 'Femmina')])
    else:
        await bot.send_message(chat, 'Hai già impostato il tuo genere su {}'.format(my_dict['Gender']))


async def anni(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    my_dict = await opendict(uid)
    if my_dict['Age'] != "Imposta la tua età con /anni" and my_dict['Age'] != "":
        await bot.send_message(chat, 'Hai già impostato la tua età a {} anni!'.format(my_dict['Age']))
    else:
        async with bot.conversation(chat) as conv:
            await conv.send_message('Quanti anni hai?')
            answer = None
            while answer != uid:
                response = await conv.get_response()
                try:
                    answer = response.from_id.user_id
                except NameError:
                    answer = response.peer_id.user_id
            ann = response.text
            if not ann.isdecimal():
                await bot.send_message(chat, 'L\'età deve essere un numero!')
                await anni(event)
            else:
                await bot.send_message(chat, 'Hai impostato la tua età a {}'.format(ann))
                my_dict["Age"] = ann
                await writedict(uid, my_dict)


async def pickloot():
    base = (0, 2.5, 5, 7.5, 15, 25, 45)
    rarity = random.choices(raritylist, weights=base, k=2)
    loot = random.choice([item for item in oggetti if str(rarity[0]) in item and 'usabile' not in item])
    adloot = random.choice([item for item in oggetti if str(rarity[1]) in item and 'usabile' not in item])
    bonusloot = random.choice([item for item in oggetti if 'usabile' in item])
    return loot, rarity, bonusloot, adloot


async def cerca(event):
    dt_string = await nowtime()
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    bonus = False
    uid = (await event.get_sender()).id
    if randint(1, 100) <= 5:
        bonus = True
    if sender in sonno:
        await bot.send_message(uid, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        my_dict = await opendict(uid)
        att_cerca = my_dict["Stop"]
        if att_cerca:
            await bot.send_message(chat, "Devi aspettare ancora un po'...")
        else:
            loot, rarity, bonusloot, adloot = await pickloot()
            y = random.choice([loot, adloot])
            if "[S]" in y:
                text = sender + " stai lavorando tranquillamente alla tua scrivania quando con tua estrema sorpresa" \
                                " vedi entrare dalla porta **{}**.".format(y) \
                                + ("\nStranamente decide di donarti **{}**".format(bonusloot) if bonus else "") \
                                + "\nControlla il tuo zaino con /zaino"
                await bot.send_message(uid, text)
            else:
                text = sender + " , anche se il capo non vuole, stai scavando nell'armadio degli oggetti smarriti" \
                                " quando trovi **{}** e senza fare troppi complimenti decidi che adesso ti" \
                                " appartine.".format(y) \
                       + ("\nStranamente hai trovato anche **{}**".format(bonusloot) if bonus else "") \
                       + "\n\nControlla il tuo zaino con /zaino"
                textalter = sender + " , anche se il capo non vuole, stai scavando nell'armadio degli oggetti smarriti" \
                                     " quando trovi **{}** e **{}**, potendone prendere solo uno ci pensi su qualche" \
                                     " secondo e decidi che **{}** è la scelta migliore.".format(loot, adloot, y) \
                                   + ("\nStranamente hai trovato anche **{}**".format(bonusloot) if bonus else "") \
                                   + "\n\nControlla il tuo zaino con /zaino"
                chtext = random.choice([text, textalter])
                await bot.send_message(uid, chtext)
            my_dict["Inventario"] += [y] + ([bonusloot] if bonus else [])
            print(dt_string, sender, "trova", y, " - Bonus:", bonusloot if bonus else bonus)
            my_dict["Stop"] = True
            await writedict(uid, my_dict)
            await aspettacerca(uid)


async def aspettacerca(uid):
    await asyncio.sleep(60)
    my_dict = await opendict(uid)
    my_dict["Stop"] = False
    await writedict(uid, my_dict)
    await bot.send_message(uid, "Puoi tornare a cercare!")


async def zaino(event):
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    my_dict = await opendict(uid)
    inventario = my_dict["Inventario"]
    tot = len(inventario)
    totunici = len(set(inventario))
    sacca = "Possiedi questi oggetti ( **" + str(totunici) + " unici** / **" + str(tot) + " totali** ):\n"
    for x in raritylist:
        for item in inventario:
            if x in item:
                if item not in sacca:
                    sacca += item + " x " + str(inventario.count(item)) + "\n"
    await bot.send_message(chat, sacca)


async def additem(event):
    dt_string = await nowtime()
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
            oggettisort = []
            for x in raritylist:
                for item in oggetti:
                    if x in item:
                        if item not in oggettisort:
                            oggettisort.append(item)
            with open('oggetti.json', 'w') as fileitem:
                json.dump(oggettisort, fileitem)
            with open('oggetti.json') as fileitem:
                oggetti = json.load(fileitem)
            await bot.send_message(chat, "Ho aggiunto {} all'elenco!".format(arg))
            print(dt_string, oggetti)


async def cercaoggetto(event):
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    my_dict = await opendict(uid)
    inventario = my_dict["Inventario"]
    parts = event.raw_text.split(" ", 1)
    if len(parts) <= 1:
        await bot.send_message(chat, "Per cercare un oggeto usa /oggetti <Oggetto>")
    else:
        arg = parts[1].lower()
        if len(arg) < 2:
            await bot.send_message(chat, "Mi servono almeno 2 lettere per cercare un oggetto!")
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


async def totoggetti(event):
    chat = await event.get_input_chat()
    parts = event.raw_text.split(" ", 1)
    if len(parts) <= 1:
        await bot.send_message(chat, "Per cercare un oggeto usa /oggetti <Oggetto>")
    else:
        arg = parts[1].lower()
        if len(arg) < 2:
            await bot.send_message(chat, "Mi servono almeno 2 lettere per cercare un oggetto!")
        else:
            tot = []
            for key, value in registrati.items():
                my_dict = await opendict(value)
                list2 = my_dict["Inventario"]
                tot.extend(list2)
            matches = [match for match in tot if arg in match.lower()]
            if not matches:
                await bot.send_message(chat, "Nessun oggetto trovato!")
            else:
                text = "Sono presenti in gioco:\n"
                for match in matches:
                    if match not in text:
                        num = matches.count(match)
                        text += str(match) + " x " + str(num) + "\n"
                await bot.send_message(chat, text)


async def daioggetto(event):
    dt_string = await nowtime()
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    if sender in sonno:
        await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        parts = event.raw_text.split(" ", 2)
        if len(parts) < 2:
            await bot.send_message(chat, "Per dare un oggeto usa /dai <Giocaotre> <Oggetto>")
        else:
            cont = parts[1]
            gift = parts[2].lower()
            if cont not in registrati:
                await bot.send_message(chat, "Non ho trovato questo giocatore!")
            else:
                my_dict = await opendict(uid)
                inventario = my_dict["Inventario"]
                cercagift = [matchx for matchx in inventario if gift in matchx.lower()]
                if not cercagift:
                    await bot.send_message(chat, "Non possiedi questo oggetto!")
                else:
                    if len(set(cercagift)) > 1:
                        await bot.send_message(chat, "Troppi oggetti con quel nome!")
                    else:
                        pr_gift = cercagift[0]
                        idricevente = registrati[cont]
                        my_dict = await opendict(uid)
                        my_dict["Inventario"].remove(pr_gift)
                        await writedict(uid, my_dict)
                        await event.reply("Hai dato {} a {}!".format(pr_gift, cont))
                        my_dict = await opendict(idricevente)
                        my_dict["Inventario"].append(pr_gift)
                        await writedict(idricevente, my_dict)
                        await bot.send_message(idricevente, "{} ti ha dato {}!".format(sender, pr_gift))
                        print(dt_string, sender + " ha dato " + pr_gift + " a " + cont)


async def giveitem(event):
    dt_string = await nowtime()
    global registrati
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    parts = event.raw_text.split(" ", 3)
    if len(parts) != 4:
        await bot.send_message(chat, "Per dare un oggeto usa /dai <Giocaotre> <Oggetto> <Quantità>")
    else:
        cont = parts[1]
        gift = parts[2].lower()
        count = parts[3]
        if cont not in registrati:
            await bot.send_message(chat, "Non ho trovato questo giocatore!")
        else:
            cercagift = [matchx for matchx in oggetti + usabili if gift in matchx.lower()]
            if not cercagift:
                await bot.send_message(chat, "Oggetto sconosciuto!")
            else:
                if not count.isdecimal():
                    await bot.send_message(chat, "Non hai specificato un numero valido per la quantità!")
                else:
                    if len(set(cercagift)) > 1:
                        await bot.send_message(chat, "Troppi oggetti con quel nome!")
                    else:
                        pr_gift = cercagift[0]
                        idricevente = registrati[cont]
                        await event.reply("Hai dato {} x {} a {}!".format(count, pr_gift, cont))
                        for i in range(int(count)):
                            my_dict = await opendict(idricevente)
                            my_dict["Inventario"].append(pr_gift)
                            await writedict(idricevente, my_dict)
                        await bot.send_message(idricevente, "{} ti ha dato {} x {}!".format(sender, count, pr_gift))
                        print(dt_string, sender + " ha dato " + count + " x " + pr_gift + " a " + cont)


async def lancia(event):
    uid = (await event.get_sender()).id
    sender = (await event.get_sender()).username
    my_dict = await opendict(uid)
    chat = await event.get_input_chat()
    if sender in sonno:
        await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        att_lancio = my_dict["Lancio"]
        parts = event.raw_text.split(" ", 2)
        if att_lancio:
            if event.is_group:
                await event.reply("Ti devi ancora riprendere dall\'ultimo lancio!")
            else:
                await bot.send_message(chat, "Ti devi ancora riprendere dall\'ultimo lancio!")
        elif sender in infermeria:
            if event.is_group:
                await event.reply("Non hai un bell'aspetto, aspetta di riprenderti un po' prima di lanciare oggetti!")
            else:
                await bot.send_message(uid, "Non hai un bell'aspetto, aspetta di riprenderti un po' prima di"
                                            " lanciare oggetti!")
        else:
            if len(parts) != 2:
                await bot.send_message(chat, "Per lanciare un oggeto usa /lancia <Giocaotre>")
            else:
                target = parts[1]
                if target not in registrati:
                    await bot.send_message(chat, "Lanciare oggetti è pericoloso,"
                                                 " scrivi per bene il nome di chi vuoi colpire!")
                elif target in infermeria:
                    await bot.send_message(chat, "{} non sembra avere un bell'aspetto, lasciamo che "
                                                 "riposi!".format(target))
                else:
                    inventory = my_dict["Inventario"]
                    quiver = []
                    subquiver = []
                    for item in inventory:
                        if item in bullets:
                            quiver += [item + " (" + str(inventory.count(item)) + ")"]
                            for x in quiver:
                                if x not in subquiver:
                                    subquiver.append(x)
                    keyboard = []
                    for item in subquiver:
                        data = str(uid) + "_" + item.split(" ")[1] + "_" + target
                        newdata = data.encode("ascii")
                        keyboard += [[Button.inline("1x " + item, newdata)]]
                    data = str(uid) + "Annulla"
                    newdata = data.encode("ascii")
                    keyboard += [[Button.inline("Annulla", newdata)]]
                    text = "Quale oggetto vuoi lanciare a {}?".format(target)
                    await bot.send_message(chat, text, buttons=keyboard)


async def controllohp(target, event):
    dt_string = await nowtime()
    global registrati
    print(dt_string, "Controllo HP" + str(target))
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    idtarget = registrati[target]
    print(dt_string, "Controllo HP" + str(idtarget))
    gruppo = event.is_group
    my_dict = await opendict(idtarget)
    vita = my_dict["HP"]
    if vita <= 0:
        infermeria.append(target)
        print(dt_string, infermeria, "ingresso", target)
        await bot.send_message(idtarget, "L'ultimo colpo ti ha fatto perdere i sensi, vieni portato in infermeria!")
        await bot.send_message(uid, "Con il tuo ultimo colpo hai spedito {} in infermeria!".format(target))
        if gruppo:
            await bot.send_message(chat, "{} cade al suolo senza sensi!".format(target))
        await asyncio.sleep(900)
        if target in infermeria:
            infermeria.remove(target)
            print(dt_string, infermeria, "uscita", target)
            my_dict = await opendict(idtarget)
            my_dict["HP"] = 50
            await writedict(idtarget, my_dict)
            await bot.send_message(idtarget, "Ti sgranchisci le gambe ed esci dall'infermeria!")
            if gruppo:
                await bot.send_message(chat, "{} è di nuovo in piena forma!".format(target))


async def aspettalancia(uid):
    dt_string = await nowtime()
    print(dt_string, "Inizo atetsa lancio", uid)
    await asyncio.sleep(45)
    my_dict = await opendict(uid)
    att_lancio = my_dict["Lancio"]
    print(dt_string, "Attesa lancio pre", att_lancio, uid)
    my_dict["Lancio"] = False
    print(dt_string, "Attesa lancio post", my_dict["Lancio"], uid)
    await writedict(uid, my_dict)
    await bot.send_message(uid, "Puoi lanciare un altro oggetto!")


async def freccetta(target, event, uid):
    sonno.append(target)
    print(sonno)
    await bot.send_message(target, "Sei stato colpito da una freccetta tranquillante "
                                   "e sei caduto in un sonno profondo!")
    await event.edit("Hai colpito {}, lo vedi cadere al suolo addormentato!".format(target))
    await aspettalancia(uid)
    await asyncio.sleep(255)
    if target in sonno:
        sonno.remove(target)
        print(sonno)
        await bot.send_message(target, "Abbastanza intontito, finalmente riesci a risprire gli occhi!")


async def furto(event):
    dt_string = await nowtime()
    global rapina
    global ladro
    ladro = (await event.get_sender()).username
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    if event.is_group:
        message = event.message
        await message.delete()
        await bot.send_message(chat, "Meglio usarlo in privato...")
    else:
        if rapina:
            await bot.send_message(uid, "C'è già un furto in corso, i tuoi misfatti dovranno attendere!")
        elif ladro in sonno:
            await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
        else:
            global refurtiva
            vittima = random.choice([n for n in list(registrati.keys()) if n not in ladro])
            idtarget = registrati[vittima]
            my_dict = await opendict(idtarget)
            sacca = my_dict["Inventario"]
            uid = (await event.get_sender()).id
            if ladro in infermeria:
                await bot.send_message(ladro, "Sei in infermeria, non è il caso di tentare un furto!")
            else:
                prob = randint(1, 10)
                if not sacca:
                    await bot.send_message(ladro, "Ti è anadata male, la tua vittima ha lo zaino vuoto!")
                else:
                    refurtiva = random.choice([matchx for matchx in sacca if '[Admin]' not in matchx])
                    my_dict["Inventario"].remove(refurtiva)
                    await writedict(idtarget, my_dict)
                    my_dict = await opendict(uid)
                    my_dict["Inventario"] += [refurtiva]
                    await writedict(uid, my_dict)
                    if prob >= 5 and vittima not in sonno:
                        rapina = True
                        print(dt_string, ladro, vittima, refurtiva, "Ha lasciato tracce...", "rapina impostato su", str(rapina))
                        await bot.send_message(ladro, "Hai rubato {} a {} ma hai lasciato delle tracce dietro "
                                                      "di te!".format(refurtiva, vittima))
                        await bot.send_message(vittima, "Senti lo zaino stranamente leggero e dopo pochi istanti ti "
                                                        "accorgi che effettivamente ti manca {}".format(refurtiva),
                                               buttons=[Button.inline('Indaga 🔍', b'indaga')])
                    else:
                        print(dt_string, ladro, vittima, refurtiva, "Non ha lasciato tracce...")
                        await bot.send_message(ladro, "Hai rubato {} a {} e te la sei svignata "
                                                      "agevolmente!".format(refurtiva, vittima))
                        if vittima in sonno:
                            sonno.remove(vittima)
                            await bot.send_message(vittima, "Dei rumori sospetti ti hanno svegliato, "
                                                            "ma non noti nulla di strano...")


async def useitem(event):
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    if sender in infermeria or sender in sonno:
        my_dict = await opendict(uid)
        inventario = my_dict["Inventario"]
        frominventory = [matchx for matchx in inventario if 'piuma' in matchx.lower()]
        if frominventory:
            container = []
            subcontainer = []
            for item in frominventory:
                container += [item + " (" + str(frominventory.count(item)) + ")"]
                for x in container:
                    if x not in subcontainer:
                        subcontainer += [x]
            keyboard = []
            for item in subcontainer:
                data = str(uid) + item.split(" ")[1]
                newdata = data.encode("ascii")
                keyboard += [[Button.inline("1x " + item, newdata)]]
            data = str(uid) + "Annulla"
            newdata = data.encode("ascii")
            keyboard += [[Button.inline("Annulla", newdata)]]
            text = "Quale oggetto vuoi usare?"
            await bot.send_message(chat, text, buttons=keyboard)
        else:
            await bot.send_message(chat, "In questo momento non puoi usare oggetti!")
    else:
        my_dict = await opendict(uid)
        inventario = my_dict["Inventario"]
        frominventory = [matchx for matchx in inventario if '[usabile]' in matchx.lower()]
        container = []
        subcontainer = []
        for item in frominventory:
            container += [item + " (" + str(frominventory.count(item)) + ")"]
            for x in container:
                if x not in subcontainer:
                    subcontainer += [x]
        keyboard = []
        for item in subcontainer:
            data = str(uid)+item.split(" ")[1]
            newdata = data.encode("ascii")
            keyboard += [[Button.inline("1x " + item, newdata)]]
        data = str(uid) + "Annulla"
        newdata = data.encode("ascii")
        keyboard += [[Button.inline("Annulla", newdata)]]
        text = "Quale oggetto vuoi usare?"
        await bot.send_message(chat, text, buttons=keyboard)


@bot.on(events.CallbackQuery())
async def usehandler(event):
    uid = (await event.get_sender()).id
    check = event.data.decode("ascii")
    sender = (await event.get_sender()).username
    if str(uid) in check:
        if "Annulla" in check:
            await event.edit('Operazione annullata!')
            return
        if "pozione" in check:
            x = "una pozione rossa [R] [usabile]"
            my_dict = await opendict(uid)
            hp = my_dict['HP']
            print(hp)
            if hp == 50:
                await event.edit("Le pozioni sono rare, meglio non usarla quando sei già in forma!")
            else:
                cura = randint(1, 20)
                postcura = hp + cura
                if postcura <= 50:
                    my_dict["HP"] = postcura
                else:
                    my_dict["HP"] = 50
                my_dict["Inventario"].remove(x)
                await writedict(uid, my_dict)
                await event.edit("Ti sei curato di {} HP, adesso hai {} HP!".format(cura, my_dict["HP"]))
                return
        elif "piuma" in check:
            if sender not in infermeria:
                await event.edit("Sei in buona salute, non ti connviene sprecare una piuma!")
            else:
                x = "una piuma di fenice [L] [usabile]"
                my_dict = await opendict(uid)
                my_dict["HP"] = 25
                my_dict["Inventario"].remove(x)
                await writedict(uid, my_dict)
                await event.edit("Consumi la piuma e ti senti subito meglio!")
                infermeria.remove(sender)
                return
        elif "goccia" in check:
            await event.edit("Non si sa ancora a cosa possa servire questo oggetto!")
        elif "raggio" in check:
            await event.edit("Non si sa ancora a cosa possa servire questo oggetto!")


@bot.on(events.CallbackQuery())
async def throwhandler(event):
    uid = (await event.get_sender()).id
    check = event.data.decode("ascii")
    sender = (await event.get_sender()).username
    databullet = check.split("_")[1]
    bullet = [matchx for matchx in bullets if databullet in matchx][0]
    target = check.split("_")[2]
    idtarget = registrati[target]
    if "freccetta" in check:
        my_dict = await opendict(uid)
        my_dict["Inventario"].remove(bullet)
        my_dict["Lancio"] = True
        await writedict(uid, my_dict)
        await freccetta(target, event, uid)
        return
    elif "energetica" in check:
        my_dict = await opendict(idtarget)
        vita = int(my_dict["HP"])
        danni = vita
        my_dict["HP"] = vita - danni
        await writedict(idtarget, my_dict)
        await event.edit("Hai lanciato {} a {} e gli hai tolto {} HP!".format(bullet, target, danni))
        await bot.send_message(idtarget, "{} ti ha lanciato {} e ti ha "
                                         "tolto {} HP!".format(sender, bullet, danni))
        if event.is_group:
            await event.edit("{} ha lanciato {} a {} e gli ha tolto {} HP!".format(sender, bullet, target, danni))
        await controllohp(target, event)
    elif "urna" in check:
        my_dict = await opendict(uid)
        my_dict["Inventario"].remove(bullet)
        my_dict["Lancio"] = True
        await writedict(uid, my_dict)
        await event.edit("L'antica urna va in mille pezzi sui piedi di {}!".format(target))
        await bot.send_message(idtarget, "L'antica urna lanciata da {} va in frantumi sui tuoi piedi e subito dopo"
                                         " uno strano spettro con un cucchiaio in mano appare davanti"
                                         " a te!".format(sender, bullet))
        if event.is_group:
            await event.edit("L'antica urna lanciata da {} va in mille pezzi sui"
                             " piedi di {}!".format(sender, target))
        cursed.append(target)
        await aspettalancia(uid)
        await curse(event, target, bullet)
        return
    elif "cofanetto" in check:
        my_dict = await opendict(uid)
        my_dict["Inventario"].remove(bullet)
        my_dict["Lancio"] = True
        await writedict(uid, my_dict)
        await event.edit("Il cofanetto vellutato cade per terra e si spalanca davanti ai piedi di {}!".format(target))
        await bot.send_message(idtarget, "Il cofanetto vellutato lanciato da {} cade davanti ai tuoi piedi e si apre,"
                                         " subito dopo uno strano spettro con un dildo borchiato in mano appare"
                                         " davanti a te!".format(sender, bullet))
        if event.is_group:
            await event.edit("Il cofanetto vellutato lanciato da {} cade a terra e si apre davanti ai"
                             " piedi di {}!".format(sender, target))
        cursed.append(target)
        await aspettalancia(uid)
        await curse(event, target, bullet)
        return
    else:
        danni = randint(1, 6)
        my_dict = await opendict(uid)
        my_dict["Inventario"].remove(bullet)
        my_dict["Lancio"] = True
        await writedict(uid, my_dict)
        await event.edit("Hai lanciato {} a {} e gli hai tolto {} HP!".format(bullet, target, danni))
        my_dict = await opendict(idtarget)
        vita = int(my_dict["HP"])
        my_dict["HP"] = vita - danni
        await writedict(idtarget, my_dict)
        await bot.send_message(idtarget, "{} ti ha lanciato {} e ti ha "
                                         "tolto {} HP!".format(sender, bullet, danni))
        if event.is_group:
            await event.edit("{} ha lanciato {} a {} e gli ha tolto {} HP!".format(sender, bullet, target, danni))
        if target in sonno:
            sonno.remove(target)
            await bot.send_message(target, "Il colpo ti ha svegliato!")
        await controllohp(target, event)
        await aspettalancia(uid)


async def edititem(event):
    dt_string = await nowtime()
    chat = await event.get_input_chat()
    parts = event.raw_text.split(" ", 2)
    if len(parts) <= 2:
        await bot.send_message(chat, "Per cercare un oggeto usa /edititem <Oggetto> <Modifica>")
    else:
        arg = parts[1]
        new = parts[2]
        if len(arg) < 3:
            await bot.send_message(chat, "Mi servono almeno 3 lettere per cercare un oggetto!")
        else:
            for idx, item in enumerate(oggetti):
                if arg in item:
                    oggetti[idx] = new
                    with open('oggetti.json', 'w') as fileitem:
                        json.dump(oggetti, fileitem)
            for key, value in registrati.items():
                my_dict = await opendict(value)
                list2 = my_dict["Inventario"]
                for idx, item in enumerate(list2):
                    if arg in item:
                        my_dict["Inventario"][idx] = new
                        await writedict(value, my_dict)
        text = "Hai modificato le occorrenze di " + arg + " in " + new
        print(dt_string, text)
        await bot.send_message(chat, text)


async def invitems(event):
    chat = await event.get_input_chat()
    tot = len(set(oggetti))
    text = "Oggetti attualmente in gioco ({}):".format(tot)
    for item in oggetti:
        text += "\n" + item
    await bot.send_message(chat, text)


async def curse(event, target, bullet):
    dt_string = await nowtime()
    chat = await event.get_input_chat()
    targetid = registrati[target]
    if target in infermeria:
        await bot.send_message(chat, "Il tuo obbiettivo è già malconcio, lo spettro dopo qualche secondo "
                                     "svanisce nel nulla!")
        cursed.remove(target)
        return
    else:
        my_dict = await opendict(targetid)
        while my_dict["HP"] > 0:
            await asyncio.sleep(300)
            my_dict["HP"] -= 1
            await writedict(targetid, my_dict)
            if "urna" in bullet:
                await bot.send_message(targetid, "Lo strano spettro ti colpisce con il cucchiaio e ti leva 1 HP!")
            else:
                if randint(1, 100) <= 30:
                    await bot.send_message(targetid, "Lo strano spettro ti colpisce con il dildo borchiato e ti leva"
                                                     " 1 HP!")
                else:
                    await bot.send_message(targetid, "Un colpo netto di dildo e vieni in modo mostruoso innaffiando lo"
                                                     " spettro che svanisce sogghignando!")
                    cursed.remove(target)
                    my_dict = await opendict(targetid)
                    my_dict["HP"] += 20
                    await writedict(targetid, my_dict)
                    await bot.send_message(targetid, "L'esperienza è stata strana ma piacevole, ti senti in forma!")
                    return
        infermeria.append(target)
        print(dt_string, infermeria, "ingresso", target)
        await bot.send_message(targetid, "Un ultimo colpo e vedi lo spettro svanire mentre crolli a terra!")
        await asyncio.sleep(900)
        if target in cursed:
            cursed.remove(target)
        if target in infermeria:
            infermeria.remove(target)
            print(dt_string, infermeria, "uscita", target)
            my_dict = await opendict(targetid)
            my_dict["HP"] = 50
            await writedict(targetid, my_dict)
            await bot.send_message(targetid, "Ti sgranchisci le gambe ed esci dall'infermeria!")
            if event.is_group:
                await bot.send_message(chat, "{} è di nuovo in piena forma!".format(target))


@bot.on(events.NewMessage(pattern=r'(?i).*heck'))
async def handler(event):
    await event.delete()
    sender = await event.get_sender()
    print("Deleted: " + event.raw_text + " sent by " + sender.username + " " + str(event.sender_id))


with bot:
    @bot.on(events.NewMessage)
    async def handler(event):
        print(event)
        #  global lastmessage
        #  lastmessage = event.raw_text
        sender = (await event.get_sender()).username
        if sender == owner:
            if event.raw_text.startswith("/additem"):
                await additem(event)
            elif event.raw_text.startswith("/giveitem"):
                await giveitem(event)
            elif event.raw_text.startswith("/edititem"):
                await edititem(event)
            elif 'hello' in event.raw_text:
                await event.reply('hi!')
            elif event.raw_text.startswith("#VARINFO"):
                stringa = 'Infermeria: ' + str(infermeria) + '\n'
                stringa += 'Sonno: ' + str(sonno) + '\n'
                stringa += 'Maledizione: ' + str(cursed) + '\n'
                stringa += 'Rapina: ' + str(rapina) + '\n'
                stringa += 'Ladro: ' + str(ladro) + '\n'
                stringa += 'Refurtiva: ' + str(refurtiva) + '\n'
                await bot.send_message(sender, stringa)
            elif event.raw_text.startswith("/inv_items"):
                await invitems(event)
        if event.raw_text.startswith("/start") or event.raw_text.startswith("/via"):
            await start(event)
        elif sender in registrati:
            if event.raw_text.startswith("/sesso"):
                await sesso(event)
            elif event.raw_text.startswith("/scheda"):
                await scheda(event)
            elif event.raw_text.startswith("/anni"):
                await anni(event)
            elif event.raw_text.startswith("/cerca"):
                await cerca(event)
            elif event.raw_text.startswith("/zaino"):
                await zaino(event)
            elif event.raw_text.startswith("/oggetto"):
                await cercaoggetto(event)
            elif event.raw_text.startswith("/oggetti"):
                await totoggetti(event)
            elif event.raw_text.startswith("/dai"):
                await daioggetto(event)
            elif event.raw_text.startswith("/lancia"):
                await lancia(event)
            elif event.raw_text.startswith("/ruba"):
                await furto(event)
            elif event.raw_text.startswith("/usa"):
                await useitem(event)
        else:
            if event.is_group:
                return
            else:
                await bot.send_message(sender, "Prima di poter usare qualunque comando ti devi registrare con /start")
#        Comando di test per varie funzioni
#        if '/test' in event.raw_text:
#            await test()
#            await lancia(event)
#            chat = await event.get_input_chat()
#            text = "Hai rotto il cazzo"
#            await bot.send_message(chat, text, buttons=[[Button.inline(text='una pozione rossa [C]', data=b'risp1')],
#                                                       [Button.inline(text='Pipì', data=b'risp2')]])
#            await bot.send_message(chat, text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
