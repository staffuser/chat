import asyncio
import datetime
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server, config
from pywebio.session import run_js, local as session_local
from pywebio.session import defer_call, info as session_info, run_async, run_js

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100
               
async def main():
    global chat_msgs
    put_markdown('#🧊 Добро пожаловать в онлайн чат!')
    session_local.curr_row = 0
    session_local.curr_word = ''
    session_local.green_chars = set()
    session_local.game_pass = False
    session_local.game_result = ''

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Войти в чат", required=True, placeholder="Ваше имя", validate=lambda n: "Такой ник уже используется!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msgs.append(('📢', f'`{nickname}` присоединился к чату!'))
    msg_box.append(put_markdown(f'📢 `{nickname}` присоединился к чату'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 Новое сообщение", [
            input(placeholder="Текст сообщения ...", name="msg"),
            actions(name="cmd", buttons=["Отправить", {'label': "Выйти из чата", 'type': 'cancel'}])
        ], validate = lambda m: ('msg', "Введите текст сообщения!") if m["cmd"] == "Отправить" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("Вы вышли из чата!")
    msg_box.append(put_markdown(f'1 📢 Пользователь `{nickname}` покинул чат!'))
    chat_msgs.append(('📢', f'2 Пользователь `{nickname}` покинул чат!'))

    put_buttons(['Перезайти'], onclick=lambda btn:run_js('window.location.reload()'))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)
        
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname: # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
        
        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]
        
        last_idx = len(chat_msgs)

def process_http_request(environ, start_response):
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/html; charset=utf-8'),
    ]
    start_response(status, response_headers)
    html_as_bytes = HTML.encode('utf-8')
def on_key_press(char):

    session_local.game_result += '\n'

    session_local.curr_row += 1
    session_local.curr_word = ''

    if session_local.game_pass:
        message = f'Wordle {session_local.curr_row}\n' + session_local.game_result
        with popup("Game Result", size='small'):
            put_text(message).style('text-align: center')
            put_button('Share', color='success', onclick=lambda: toast('Copied to clipboard') or run_js("""navigator.clipboard.write([new ClipboardItem({"text/plain":new Blob([text],{type:"text/plain"})})]);""", text=message)).style('text-align: center')
 
if __name__ == "__main__":
    import socket
    start_server(main,title="Сhat from the creators.", description="The ALIENATING server", host="localhost", debug=True, port=8080, cdn=False)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
    s.close()   
    address = ("", 80)
    server = http.server.HTTPServer(address, http.server.CGIHTTPRequestHandler)
    server.serve_forever()
