"""
MIT License

Copyright (c) 2021 madboy482

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
import json

from pyrogram import Client, Filters
from pyrogram import (InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      CallbackQuery)

import functions as func
import raid_dynamax as raid

from Vars import Var

PokeDex = Client(
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.TOKEN,
    session_name='MadBoy482 PokeDex'
)

texts = json.load(open('PokeDex/text.json', 'r'))
data = json.load(open('PokeDex/poke.json', 'r'))
stats = json.load(open('PokeDex/stats.json', 'r'))
ptype = json.load(open('PokeDex/types.json', 'r'))

usage_dict = {'vgc': None}
raid_dict = {}



# ===== Stats ===== #
@PokeDex.on_message(Filters.private & Filters.create(lambda _, message: str(message.chat.id) not in stats['users']))
@PokeDex.on_message(Filters.group & Filters.create(lambda _, message: str(message.chat.id) not in stats['groups']))
def get_bot_data(PokeDex, message):
    cid = str(message.chat.id)
    if message.chat.type == 'private':
        stats['users'][cid] = {}
        name = message.chat.first_name
        try:
            name = message.chat.first_name + ' ' + message.chat.last_name
        except TypeError:
            name = message.chat.first_name
        stats['users'][cid]['name'] = name
        try:
            stats['users'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    elif message.chat.type in ['group', 'supergroup']:
        stats['groups'][cid] = {}
        stats['groups'][cid]['title'] = message.chat.title
        try:
            stats['groups'][cid]['username'] = message.chat.username
        except AttributeError:
            pass
        stats['groups'][cid]['members'] = PokeDex.get_chat(cid).members_count

    json.dump(stats, open('PokeDex/stats.json', 'w'), indent=4)
    print(stats)
    print('\n\n')
    message.continue_propagation()


@PokeDex.on_message(Filters.command(['stats', 'stats@PokeDex_RoBot']))
def get_stats(PokeDex, message):
    if message.from_user.id in Var.ACCESS:
        members = 0
        for group in stats['groups']:
            members += stats['groups'][group]['members']
        text = texts['stats'].format(
            len(stats['users']),
            len(stats['groups']),
            members
        )
        PokeDex.send_message(
            chat_id=message.chat.id,
            text=text
        )

        

# ===== Home Menu ===== #
@PokeDex.on_message(Filters.command(['start', 'start@PokeDex_RoBot']))
def start(PokeDex, message):
    PokeDex.send_message(
        chat_id=message.chat.id,
        text=texts['start_message'],
        parse_mode='HTML'
    )

    
    
# ==== Types of Pokemons ===== #
@PokeDex.on_message(Filters.command(['type', 'type@PokeDex_RoBot']))
def ptype(PokeDex, message):
    try:
        gtype = message.text.split(' ')[1]
    except IndexError as s:
        PokeDex.send_message(
            chat_id=message.chat.id,
            text=("**Syntax Error :** __Correct Syntax »__ `'/type pokemon_type'`\n"
                  "__Eg »__ `/type fairy`")
        )
        return
    try:
        data = ptype[gtype.lower()]
    except KeyError as s:
        PokeDex.send_message(
            chat_id=message.chat.id,
            text=("**Hmm, I checked in all the Pokemon Databases for the requested type, but found nothing :/ **\n"
                  "**Try doing**  `/types`  **to check for the existing types.**")
        )
        return
    strong_against = ", ".join(data['strong_against'])
    weak_against = ", ".join(data['weak_against'])
    resistant_to = ", ".join(data['resistant_to'])
    vulnerable_to = ", ".join(data['vulnerable_to'])
    keyboard = ([[
        InlineKeyboardButton('« All Types »',callback_data=f"hexa_back_{message.from_user.id}")]])
    PokeDex.send_message(
        chat_id=message.chat.id,
        text=(f"**Type :**\n`{gtype.lower()}`\n\n"
              f"**Strong Against :**\n`{strong_against}`\n\n"
              f"**Weak Against :**\n`{weak_against}`\n\n"
              f"**Resistant To :**\n`{resistant_to}`\n\n"
              f"**Vulnerable To :**\n`{vulnerable_to}`\n\n"
              f"**𝑰𝒏𝒇𝒐 𝒈𝒂𝒕𝒉𝒆𝒓𝒆𝒅 𝒃𝒚 @PokeDex_RoBot**"),
        reply_markup=InlineKeyboardMarkup(keyboard)
           
    )

    
    
# ==== Pokemon Types List ===== #
def ptype_buttons(user_id):
    keyboard = ([[
        InlineKeyboardButton('🔶 Normal 🔶',callback_data=f"type_normal_{user_id}"),
        InlineKeyboardButton('🥊 Fighting 🥊',callback_data=f"type_fighting_{user_id}"),
        InlineKeyboardButton('🌪 Flying 🌪',callback_data=f"type_flying_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('☣️ Poison ☣️',callback_data=f"type_poison_{user_id}"),
        InlineKeyboardButton('⛰ Ground ⛰',callback_data=f"type_ground_{user_id}"),
        InlineKeyboardButton('🧱 Rock 🧱',callback_data=f"type_rock_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('🐞 Bug 🐞',callback_data=f"type_bug_{user_id}"),
        InlineKeyboardButton('👁‍🗨 Ghost 👁‍🗨',callback_data=f"type_ghost_{user_id}"),
        InlineKeyboardButton('🛡 Steel 🛡',callback_data=f"type_steel_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('🔥 Fire 🔥',callback_data=f"type_fire_{user_id}"),
        InlineKeyboardButton('💧 Water 💧',callback_data=f"type_water_{user_id}"),
        InlineKeyboardButton('🍃 Grass 🍃',callback_data=f"type_grass_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('⚡️ Electric ⚡️',callback_data=f"type_electric_{user_id}"),
        InlineKeyboardButton('🔮 Psychic 🔮',callback_data=f"type_psychic_{user_id}"),
        InlineKeyboardButton('❄️ Ice ❄️',callback_data=f"type_ice_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('🐉 Dragon 🐉',callback_data=f"type_dragon_{user_id}"),
        InlineKeyboardButton('🧚 Fairy 🧚',callback_data=f"type_fairy_{user_id}"),
        InlineKeyboardButton('⚫️ Dark ⚫️',callback_data=f"type_dark_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('« Delete »',callback_data=f"hexa_delete_{user_id}")]])
    return keyboard
    
@PokeDex.on_message(Filters.command(['types', 'types@PokeDex_RoBot']))
def types(PokeDex, message): 
    user_id = message.from_user.id
    PokeDex.send_message(
        chat_id=message.chat.id,
        text="𝑳𝒊𝒔𝒕 𝒐𝒇 𝑻𝒚𝒑𝒆𝒔 𝒐𝒇 𝑷𝒐𝒌𝒆𝒎𝒐𝒏𝒔 :",
        reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
    )
    
    

# ===== Types Callback ==== #
@PokeDex.on_callback_query(Filters.create(lambda _, query: 'type_' in query.data))
def button(client: PokeDex, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[0]
    type_n = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if cuser_id == user_id:
        if query_data == "type":
            data = ptype[type_n]
            strong_against = ", ".join(data['strong_against'])
            weak_against = ", ".join(data['weak_against'])
            resistant_to = ", ".join(data['resistant_to'])
            vulnerable_to = ", ".join(data['vulnerable_to'])
            keyboard = ([[
            InlineKeyboardButton('« Back »',callback_data=f"hexa_back_{user_id}")]])
            callback_query.message.edit_text(
                text=(f"**Type :**\n`{type_n}`\n\n"
                f"**Strong Against :**\n`{strong_against}`\n\n"
                f"**Weak Against :**\n`{weak_against}`\n\n"
                f"**Resistant To :**\n`{resistant_to}`\n\n"
                f"**Vulnerable To :**\n`{vulnerable_to}`\n\n"
                f"**𝑰𝒏𝒇𝒐 𝒈𝒂𝒕𝒉𝒆𝒓𝒆𝒅 𝒃𝒚 @PokeDex_RoBot**"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        callback_query.answer(
            text="You're not allowed to access this Button !!",
            show_alert=True
        )
    

@PokeDex.on_callback_query(Filters.create(lambda _, query: 'hexa_' in query.data))
def button2(client: PokeDex, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if user_id == cuser_id:
        if query_data == "back":
            callback_query.message.edit_text(
                "𝑳𝒊𝒔𝒕 𝒐𝒇 𝑻𝒚𝒑𝒆𝒔 𝒐𝒇 𝑷𝒐𝒌𝒆𝒎𝒐𝒏𝒔 :",
                reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
            )
        elif query_data == "delete":
            callback_query.message.delete()
        else:
            return
    else:
        callback_query.answer(
            text="You're not allowed to access this Button !!",
            show_alert=True
        )
        
        
  
# ===== Pokemon Type Command ====== #
@PokeDex.on_message(Filters.command(['ptype', 'ptype@PokeDex_RoBot']))
def poketypes(PokeDex, message): 
    user_id = message.from_user.id
    try:
        arg = message.text.split(' ')[1].lower()
    except IndexError:
        PokeDex.send_message(
            chat_id=message.chat.id,
            text=("**Syntax Error :** __Correct Syntax »__ `'/ptype pokemon_name'`\n"
                  "__Eg »__ `/ptype Lunala`")
        )
        return  
    try:
        p_type = data[arg][arg]['type']
    except KeyError:
        PokeDex.send_message(
            chat_id=message.chat.id,
            text=("**Hmm, I checked in all the Pokemon Databases for the requested pokemon, but found nothing :/ **\n"
                  "**Try again, after checking the spelling/name of the pokemon...**")
        )
        return
    
    try:
        get_pt = f"{p_type['type1']}, {p_type['type2']:}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}"),
        InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{arg}_{user_id}")]])
    except KeyError:
        get_pt = f"{p_type['type1']}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}")]])
    PokeDex.send_message(
        chat_id=message.chat.id,
        text=(f"**Pokemon :**\n`{arg}`\n\n"
              f"**Types :**\n`{get_pt}`\n\n"
              f"__Click the button below to get the attact type effectiveness!__\n\n"
              f"**𝑰𝒏𝒇𝒐 𝒈𝒂𝒕𝒉𝒆𝒓𝒆𝒅 𝒃𝒚 @PokeDex_RoBot**"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
@PokeDex.on_callback_query(Filters.create(lambda _, query: 'poket_' in query.data))
def poketypes_callback(client: PokeDex, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    pt_name = q_data.split('_')[2]
    user_id = int(q_data.split('_')[3])  
    if callback_query.from_user.id == user_id:  
        data = ptype[query_data]
        strong_against = ", ".join(data['strong_against'])
        weak_against = ", ".join(data['weak_against'])
        resistant_to = ", ".join(data['resistant_to'])
        vulnerable_to = ", ".join(data['vulnerable_to'])
        keyboard = ([[
        InlineKeyboardButton('« Back »',callback_data=f"pback_{pt_name}_{user_id}")]])
        callback_query.message.edit_text(
            text=(f"**Type :**\n`{query_data}`\n\n"
            f"**Strong Against :**\n`{strong_against}`\n\n"
            f"**Weak Against :**\n`{weak_against}`\n\n"
            f"**Resistant To :**\n`{resistant_to}`\n\n"
            f"**Vulnerable To :**\n`{vulnerable_to}`\n\n"
            f"**𝑰𝒏𝒇𝒐 𝒈𝒂𝒕𝒉𝒆𝒓𝒆𝒅 𝒃𝒚 @PokeDex_RoBot**"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to access this Button !!",
            show_alert=True
        )
    
@PokeDex.on_callback_query(Filters.create(lambda _, query: 'pback_' in query.data))
def poketypes_back(client: PokeDex, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    user_id = int(q_data.split('_')[2]) 
    if callback_query.from_user.id == user_id:
        p_type = data[query_data][query_data]['type']
        try:
            get_pt = f"{p_type['type1']}, {p_type['type2']:}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}"),
            InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{query_data}_{user_id}")]])
        except KeyError:
            get_pt = f"{p_type['type1']}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}")]])
        callback_query.message.edit_text(
            (f"**Pokemon :**\n`{query_data}`\n\n"
             f"**Types :**\n`{get_pt}`\n\n"
             f"__Click the button below to get the attact type effectiveness!__\n\n"
             f"**𝑰𝒏𝒇𝒐 𝒈𝒂𝒕𝒉𝒆𝒓𝒆𝒅 𝒃𝒚 @PokeDex_RoBot**"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to access this Button !!",
            show_alert=True
        )
    
        
      
# ===== Data command ===== #
@PokeDex.on_callback_query(Filters.create(lambda _, query: 'basic_infos' in query.data))
@PokeDex.on_message(Filters.command(['data', 'data@PokeDex_RoBot']))
def pkmn_search(PokeDex, message):
    try:
        if message.text == '/data' or message.text == '/data@PokeDex_RoBot':
          PokeDex.send_message(message.chat.id, texts['error1'], parse_mode='HTML')
          return None
        pkmn = func.find_name(message.text)
        result = func.check_name(pkmn, data)

        if type(result) == str:
            PokeDex.send_message(message.chat.id, result)
            return None
        elif type(result) == list:
            best_matches(PokeDex, message, result)
            return None
        else:
            pkmn = result['pkmn']
            form = result['form']
    except AttributeError:
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]


    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=True)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=True)

    markup_list = [[
        InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(PokeDex, message, text, markup)


def best_matches(PokeDex, message, result):
    text = texts['results']
    emoji_list = ['1️⃣', '2️⃣', '3️⃣']
    index = 0
    for dictt in result:
        pkmn = dictt['pkmn']
        form = dictt['form']
        percentage = dictt['percentage']
        form_name = data[pkmn][form]['name']
        name = func.form_name(pkmn.title(), form_name)
        text += '\n{} <b>{}</b> (<i>{}</i>)'.format(
            emoji_list[index],
            name,
            percentage
        )
        if index == 0:
            text += ' [<b>⭐️ Top result ⭐️</b>]'
        index += 1
    PokeDex.send_message(message.chat.id, text, parse_mode='HTML')


@PokeDex.on_callback_query(Filters.create(lambda _, query: 'all_infos' in query.data))
def all_infos(PokeDex, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    
    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=False)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=False)

    markup_list = [[
        InlineKeyboardButton(
            text='➖ Reduce',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(PokeDex, call, text, markup)


@PokeDex.on_callback_query(Filters.create(lambda _, query: 'moveset' in query.data))
def moveset(PokeDex, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    if len(re.split('/', call.data)) == 4:
        page = int(re.split('/', call.data)[3])
    else:
        page = 1
    dictt = func.set_moveset(pkmn, form, page)

    func.bot_action(PokeDex, call, dictt['text'], dictt['markup'])


@PokeDex.on_callback_query(Filters.create(lambda _, query: 'locations' in query.data))
def locations(PokeDex, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]

    text = func.get_locations(data, pkmn)

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='🔙 Back to Basic Infos',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ]])

    func.bot_action(PokeDex, call, text, markup)
    


# ===== FAQ command ===== #
@PokeDex.on_message(Filters.command(['faq', 'faq@PokeDex_RoBot']))
def faq(PokeDex, message):
    text = texts['faq']
    PokeDex.send_message(
        chat_id=message.chat.id,
        text=text, 
        parse_mode='HTML',
        disable_web_page_preview=True
    )



# ===== About command ===== #
@PokeDex.on_message(Filters.command(['about', 'about@PokeDex_RoBot']))
def about(PokeDex, message):
    text = texts['about']
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='GitHub',
            url='https://github.com/madboy482/PokeDex/'
        )
    ]])

    PokeDex.send_message(
        chat_id=message.chat.id,
        text=text, 
        reply_markup=markup,
        disable_web_page_preview=True
    )


    
# ===== Presentation ===== #
@PokeDex.on_message(Filters.create(lambda _, message: message.new_chat_members))
def bot_added(PokeDex, message):
    for new_member in message.new_chat_members:
        if new_member.id == 1975640615:
            text = texts['added']
            PokeDex.send_message(
                chat_id=message.chat.id,
                text=text
            )

PokeDex.run()
