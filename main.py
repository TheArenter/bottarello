from telethon import events, TelegramClient
from telethon.tl.custom import Button
from dotenv import load_dotenv
from random import randint
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

infermeria = []
sonno = []
ladro = []
refurtiva = []
rapina = False

usabili = ["una pozione rossa [R] [usabile]"]  #  , "qualche goccia d'acqua [C] [usabile]", "un raggio di sole [C] [usabile]"]

bullets = ["un sasso [C]", "una scarpa [C]", "una matita [C]", "una cernia [R]", "un dildo glitterato [E]",
           "una mela [C]", "una zucchina ambigua [NC]", "un telecomando [C]", "un cartone di Tavernello [C]",
           "una freccetta tranquillante [S]", "un'onda energetica [Admin]", "una forchetta [C]",
           "un controller wireless PS Cinque [R]"]

raritylist = ["[S]", "[L]", "[E]", "[R]", "[NC]", "[C]"]


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
    global registrati
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    sender = (await event.get_sender()).username
    if sender:
        if sender in registrati:
            await bot.send_message(chat, "Guarda un po' chi si rivede 😊")
        else:
            print(sender + ": Ha avviato il bot")
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
    global rapina
    global ladro
    prob = randint(1, 10)
    if prob <= 5:
        print("Safe...")
        await event.edit('Purtroppo gli indizi non ti hanno portato a nulla!')
        ladro = []
        rapina = not rapina
        print(rapina)
    else:
        print("Caught...")
        idladro = registrati[ladro]
        print(idladro)
        my_dict = await opendict(idladro)
        ladrohp = my_dict["HP"]
        my_dict["HP"] = ladrohp - 10
        await writedict(idladro, my_dict)
        await event.edit('Hai scoperto il ladro, il tuo oggetto è perso, ma gli hai dato una bella lezione')
        await bot.send_message(idladro, 'Sei stato scoperto! Ti hanno dato una bella lezione ed hai perso 10 HP!')
        rapina = not rapina
        print(rapina)
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
                print(response)
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
    rarity = random.choices(raritylist, weights=(2.5, 5, 7.5, 15, 25, 45), k=1)[0]
    loot = random.choice([item for item in oggetti if str(rarity) in item])
    bonusloot = random.choice(usabili)
    return loot, rarity, bonusloot


async def cerca(event):
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    bonus = False
    if randint(1, 100) <= 5:
        bonus = True
    if sender in sonno:
        await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        uid = (await event.get_sender()).id
        my_dict = await opendict(uid)
        att_cerca = my_dict["Stop"]
        if att_cerca:
            await bot.send_message(chat, "Devi aspettare ancora un po'...")
        else:
            loot, rarity, bonusloot = await pickloot()
            if rarity == "[S]":
                text = sender + " stai lavorando tranquillamente alla tua scrivania quando con tua estrema sorpresa" \
                                " vedi entrare dalla porta **{}**.".format(loot) \
                                + ("\nStranamente decide di donarti **{}**".format(bonusloot) if bonus else "") \
                                + "\nControlla il tuo zaino con /zaino"
            else:
                text = sender + " , anche se il capo non vuole, stai scavando nell'armadio degli oggetti smarriti" \
                                " quando trovi **{}** e senza fare troppi complimenti decidi che adesso ti" \
                                " appartine.".format(loot) \
                       + ("\nStranamente hai trovato anche **{}**".format(bonusloot) if bonus else "") \
                       + "\n\nControlla il tuo zaino con /zaino"
            await bot.send_message(chat, text)
            my_dict["Inventario"] += [loot] + ([bonusloot] if bonus else [])
            print(sender, "trova", loot, " - Bonus:", bonusloot if bonus else bonus)
            my_dict["Stop"] = not att_cerca
            await writedict(uid, my_dict)
            await aspettacerca(uid)


async def aspettacerca(uid):
    await asyncio.sleep(60)
    my_dict = await opendict(uid)
    att_cerca = my_dict["Stop"]
    my_dict["Stop"] = not att_cerca
    await writedict(uid, my_dict)
    await bot.send_message(uid, "Puoi tornare a cercare!")


async def zaino(event):
    sender = (await event.get_sender()).username
    chat = await event.get_input_chat()
    uid = (await event.get_sender()).id
    my_dict = await opendict(uid)
    inventario = my_dict["Inventario"]
    tot = len(set(inventario))
    if sender in owner:
        raritylist.append('Admin')
        print(raritylist)
    sacca = "Possiedi (" + str(tot) + "):\n"
    for x in raritylist:
        for item in inventario:
            if x in item:
                if item not in sacca:
                    sacca += item + " x " + str(inventario.count(item)) + "\n"
    await bot.send_message(chat, sacca)
    raritylist.remove('Admin')


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
            print(oggetti)


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


async def totoggetti(event):
    chat = await event.get_input_chat()
    parts = event.raw_text.split(" ", 1)
    if len(parts) <= 1:
        await bot.send_message(chat, "Per cercare un oggeto usa /oggetti <Oggetto>")
    else:
        arg = parts[1].lower()
        if len(arg) < 3:
            await bot.send_message(chat, "Mi servono almeno 3 lettere per cercare un oggetto!")
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
                        print(sender + " ha dato " + pr_gift + " a " + cont)


async def giveitem(event):
    global registrati
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    parts = event.raw_text.split(" ", 3)
    print(parts)
    if len(parts) < 3:
        await bot.send_message(chat, "Per dare un oggeto usa /dai <Giocaotre> <Oggetto> <Quantità>")
    else:
        cont = parts[1]
        print(cont)
        gift = parts[2].lower()
        print(gift)
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
                        print(sender + " ha dato " + count + " x " + pr_gift + " a " + cont)


async def lancia(event):
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    if sender in sonno:
        await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        my_dict = await opendict(uid)
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
                await bot.send_message(chat, "Non hai un bell'aspetto, aspetta di riprenderti un po' prima di"
                                             " lanciare oggetti!")
        else:
            if len(parts) != 3:
                await bot.send_message(chat, "Per lanciare un oggeto usa /lancia <Giocaotre> <Oggetto>")
            else:
                target = parts[1]
                idtarget = registrati[target]
                ammo = parts[2].lower()
                if target not in registrati:
                    await bot.send_message(chat, "Lanciare oggetti è pericoloso,"
                                                 " scrivi per bene il nome di chi vuoi colpire!")
                elif target in infermeria:
                    await bot.send_message(chat, "{} non sembra avere un bell'aspetto, lasciamo che "
                                                 "riposi!".format(target))
                else:
                    my_dict = await opendict(uid)
                    inventario = my_dict["Inventario"]
                    bullet = [matchx for matchx in inventario if ammo in matchx.lower()]
                    if not bullet:
                        if event.is_group:
                            await event.reply("Non possiedi questo oggetto!")
                        else:
                            await bot.send_message(chat, "Non possiedi questo oggetto!")
                    else:
                        if len(set(bullet)) > 1:
                            if event.is_group:
                                await event.reply("Troppi oggetti con quel nome!")
                            else:
                                await bot.send_message(chat, "Troppi oggetti con quel nome!")
                        else:
                            bullet = bullet[0]
                            if bullet not in bullets:
                                if event.is_group:
                                    await event.reply("Questo non lo puoi lanciare!")
                                else:
                                    await bot.send_message(chat, "Questo non lo puoi lanciare!")
                            else:
                                if bullet == "una freccetta tranquillante [S]":
                                    print(sonno)
                                    my_dict = await opendict(uid)
                                    my_dict["Inventario"].remove(bullet)
                                    my_dict["Lancio"] = not att_lancio
                                    await writedict(uid, my_dict)
                                    await freccetta(target, chat, uid)
                                    return
                                elif bullet == "un'onda energetica [Admin]":
                                    my_dict = await opendict(idtarget)
                                    vita = int(my_dict["HP"])
                                    danni = vita
                                    my_dict["HP"] = vita - danni
                                    await writedict(idtarget, my_dict)
                                    await bot.send_message(uid, "Hai lanciato {} a {} e gli hai tolto {} HP!"
                                                           .format(bullet, target, danni))
                                    await bot.send_message(idtarget, "{} ti ha lanciato {} e ti ha "
                                                                     "tolto {} HP!".format(sender, bullet, danni))
                                    if event.is_group:
                                        await bot.send_message(chat, "{} ha lanciato {} a {} e gli ha "
                                                                     "tolto {} HP!".format(sender, bullet, target,
                                                                                           danni))
                                    await controllohp(target, event)
                                else:
                                    danni = randint(1, 6)
                                    my_dict = await opendict(uid)
                                    my_dict["Inventario"].remove(bullet)
                                    my_dict["Lancio"] = not att_lancio
                                    await writedict(uid, my_dict)
                                    await bot.send_message(uid, "Hai lanciato {} a {} e gli hai tolto {} HP!"
                                                           .format(bullet, target, danni))
                                    my_dict = await opendict(idtarget)
                                    vita = int(my_dict["HP"])
                                    my_dict["HP"] = vita - danni
                                    await writedict(idtarget, my_dict)
                                    await bot.send_message(idtarget, "{} ti ha lanciato {} e ti ha "
                                                                     "tolto {} HP!".format(sender, bullet, danni))
                                    if event.is_group:
                                        await bot.send_message(chat, "{} ha lanciato {} a {} e gli ha "
                                                                     "tolto {} HP!".format(sender, bullet, target,
                                                                                           danni))
                                    if target in sonno:
                                        sonno.remove(target)
                                        await bot.send_message(target, "Il colpo ti ha svegliato!")
                                    await controllohp(target, event)
                                    await aspettalancia(uid)


async def controllohp(target, event):
    global registrati
    print("Controllo HP" + str(target))
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    idtarget = registrati[target]
    print("Controllo HP" + str(idtarget))
    gruppo = event.is_group
    my_dict = await opendict(idtarget)
    vita = my_dict["HP"]
    if vita <= 0:
        infermeria.append(target)
        print(infermeria, "ingresso", target)
        await bot.send_message(idtarget, "L'ultimo colpo ti ha fatto perdere i sensi, vieni portato in infermeria!")
        await bot.send_message(uid, "Con il tuo ultimo colpo hai spedito {} in infermeria!".format(target))
        if gruppo:
            await bot.send_message(chat, "{} cade al suolo senza sensi!".format(target))
        await asyncio.sleep(900)
        if target in infermeria:
            infermeria.remove(target)
            print(infermeria, "uscita", target)
            my_dict = await opendict(idtarget)
            my_dict["HP"] = 50
            await writedict(idtarget, my_dict)
            await bot.send_message(idtarget, "Ti sgranchisci le gambe ed esci dall'infermeria!")
            if gruppo:
                await bot.send_message(chat, "{} è di nuovo in piena forma!".format(target))


async def aspettalancia(uid):
    print("Inizo atetsa lancio", uid)
    await asyncio.sleep(45)
    my_dict = await opendict(uid)
    att_lancio = my_dict["Lancio"]
    print("Attesa lancio pre", att_lancio, uid)
    my_dict["Lancio"] = not att_lancio
    print("Attesa lancio post", my_dict["Lancio"], uid)
    await writedict(uid, my_dict)
    await bot.send_message(uid, "Puoi lanciare un altro oggetto!")


async def freccetta(target, chat, uid):
    sonno.append(target)
    print(sonno)
    await bot.send_message(target, "Sei stato colpito da una freccetta tranquillante "
                                   "e sei caduto in un sonno profondo!")
    await bot.send_message(chat, "Hai colpito {}, lo vedi cadere al suolo "
                                 "addormentato!".format(target))
    await aspettalancia(uid)
    await asyncio.sleep(255)
    if target in sonno:
        sonno.remove(target)
        print(sonno)
        await bot.send_message(target, "Abbastanza intontito, finalmente riesci a risprire gli occhi!")


async def furto(event):
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
            print(ladro)
            global refurtiva
            vittima = random.choice([n for n in list(registrati.keys()) if n not in ladro])
            print(vittima)
            idtarget = registrati[vittima]
            print(idtarget)
            my_dict = await opendict(idtarget)
            sacca = my_dict["Inventario"]
            print(sacca)
            uid = (await event.get_sender()).id
            if ladro in infermeria:
                await bot.send_message(ladro, "Sei in infermeria, non è il caso di tentare un furto!")
            else:
                prob = randint(1, 10)
                print(prob)
                if not sacca:
                    await bot.send_message(ladro, "Ti è anadata male, la tua vittima ha lo zaino vuoto!")
                else:
                    refurtiva = random.choice(sacca)
                    print(refurtiva)
                    my_dict["Inventario"].remove(refurtiva)
                    await writedict(idtarget, my_dict)
                    my_dict = await opendict(uid)
                    my_dict["Inventario"] += [refurtiva]
                    await writedict(uid, my_dict)
                    if prob >= 5 and vittima not in sonno:
                        rapina = not rapina
                        print(ladro, vittima, refurtiva, "Ha lasciato tracce...", "rapina impostato su", str(rapina))
                        await bot.send_message(ladro, "Hai rubato {} a {} ma hai lasciato delle tracce dietro "
                                                      "di te!".format(refurtiva, vittima))
                        await bot.send_message(vittima, "Senti lo zaino stranamente leggero e dopo pochi istanti ti "
                                                        "accorgi che effettivamente ti manca {}".format(refurtiva),
                                               buttons=[Button.inline('Indaga 🔍', b'indaga')])
                    else:
                        print(ladro, vittima, refurtiva, "Non ha lasciato tracce...")
                        await bot.send_message(ladro, "Hai rubato {} a {} e te la sei svignata "
                                                      "agevolmente!".format(refurtiva, vittima))
                        if vittima in sonno:
                            sonno.remove(vittima)
                        await bot.send_message(vittima, "Dei rumori sospetti ti hanno svegliato, "
                                                        "ma non noti nulla di strano...")


async def useitem(event):
    uid = (await event.get_sender()).id
    chat = await event.get_input_chat()
    sender = (await event.get_sender()).username
    if sender in sonno:
        await bot.send_message(chat, "Stai dormendo profonfamente e non riesci a svegliarti!")
    else:
        parts = event.raw_text.split(" ", 1)
        if sender in infermeria:
            if event.is_group:
                await event.reply("Non hai abbastanza forze per usare questo oggetto!")
            else:
                await bot.send_message(chat, "Non hai abbastanza forze per usare questo oggetto!")
        else:
            if len(parts) != 2:
                await bot.send_message(chat, "Per usare un oggeto usa /usa <Oggetto>")
            else:
                usablex = parts[1].lower()
                my_dict = await opendict(uid)
                inventario = my_dict["Inventario"]
                usable = [matchx for matchx in inventario if usablex in matchx.lower()]
                if not usable:
                    if event.is_group:
                        await event.reply("Non possiedi questo oggetto!")
                    else:
                        await bot.send_message(chat, "Non possiedi questo oggetto!")
                else:
                    if len(set(usable)) > 1:
                        if event.is_group:
                            await event.reply("Troppi oggetti con quel nome!")
                        else:
                            await bot.send_message(chat, "Troppi oggetti con quel nome!")
                    else:
                        usable = usable[0]
                        if usable not in usabili:
                            if event.is_group:
                                await event.reply("Questo non lo puoi usare!")
                            else:
                                await bot.send_message(chat, "Questo non lo puoi usare!")
                        else:
                            if usable == "una pozione rossa [R] [usabile]":
                                my_dict = await opendict(uid)
                                hp = my_dict['HP']
                                print(hp)
                                if hp == 50:
                                    await bot.send_message(chat, "Le pozioni sono rare, meglio non usarla quando sei "
                                                                 "già in forma!")
                                else:
                                    cura = randint(1, 20)
                                    postcura = hp + cura
                                    if postcura <= 50:
                                        my_dict["HP"] = postcura
                                    else:
                                        my_dict["HP"] = 50
                                    my_dict["Inventario"].remove(usable)
                                    await writedict(uid, my_dict)
                                    await bot.send_message(chat, "Ti sei curato di {} HP, adesso hai {} "
                                                                 "HP!".format(cura, my_dict["HP"]))
                                    return


async def edititem(event):
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
        print("Hai modificato le occorrenze di " + arg + " in " + new)


async def invitems(event):
    chat = await event.get_input_chat()
    tot = len(set(oggetti))
    text = "Oggetti attualmente in gioco ({}):".format(tot)
    for item in oggetti:
        text += "\n" + item
    await bot.send_message(chat, text)


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
            if '/additem' in event.raw_text:
                await additem(event)
            elif '/giveitem' in event.raw_text:
                await giveitem(event)
            elif '/edititem' in event.raw_text:
                await edititem(event)
            elif 'hello' in event.raw_text:
                await event.reply('hi!')
            elif '#VARINFO' in event.raw_text:
                stringa = 'Infermeria: ' + str(infermeria) + '\n'
                stringa += 'Sonno: ' + str(sonno) + '\n'
                stringa += 'Rapina: ' + str(rapina) + '\n'
                stringa += 'Ladro: ' + str(ladro) + '\n'
                stringa += 'Refurtiva: ' + str(refurtiva) + '\n'
                await bot.send_message(sender, stringa)
            elif '/inv_items' in event.raw_text:
                await invitems(event)
        if '/start' in event.raw_text or '/vai' in event.raw_text:
            await start(event)
        elif sender in registrati:
            if '/sesso' in event.raw_text:
                await sesso(event)
            elif '/scheda' in event.raw_text:
                await scheda(event)
            elif '/anni' in event.raw_text:
                await anni(event)
            elif '/cerca' in event.raw_text:
                await cerca(event)
            elif '/zaino' in event.raw_text:
                await zaino(event)
            elif '/oggetto' in event.raw_text:
                await cercaoggetto(event)
            elif '/oggetti' in event.raw_text:
                await totoggetti(event)
            elif '/dai' in event.raw_text:
                await daioggetto(event)
            elif '/lancia' in event.raw_text:
                await lancia(event)
            elif '/ruba' in event.raw_text:
                await furto(event)
            elif '/usa' in event.raw_text:
                await useitem(event)
        else:
            await bot.send_message(sender, "Prima di poter usare qualunque comando ti devi registrare con /start")
#        Comando di test per varie funzioni
#        elif '/test' in event.raw_text:
#            chat = await event.get_input_chat()
#            text = "***"
#            await bot.send_message(chat, text, buttons=[[Button.inline(text='una pozione rossa [C]', data=b'risp1')],
#                                                        [Button.inline(text='Pipì', data=b'risp2')]])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
