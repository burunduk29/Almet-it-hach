from aiogram import types, executor, Dispatcher, Bot
from bs4 import BeautifulSoup
import requests
import openai
import cfg

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
gpt_token = "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"
openai.api_key = gpt_token


# fake user

with requests.Session() as se:
    se.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en"
    }

# start function


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(message.chat.id, text=f"<b>💊 Добро пожаловать в программу поиска аналогов лекарств!</b>\n\n"
                                                 f"🧪 Здесь мы поможем Вам найти альтернативные препараты с аналогичным действующим веществом или схожими терапевтическими свойствами\n\n"
                                                 f"💪 Наша программа сделает все возможное, чтобы предложить вам наиболее подходящие варианты замены, а также ознакомиться с их ценами.\n\n"
                                                 f"<b>📚🚑 Не забывайте, что результаты поиска являются справочной информацией и не заменяют консультацию с врачом или фармацевтом. Всегда обсуждайте с ними свои лекарственные потребности и применение аналогов.</b>\n\n"
                                                 f"<b>🔍 Удачного поиска</b>\n\n"
                                                 f"🖊️ Для начала, пожалуйста, введите название лекарства:", parse_mode="HTML")

# algorithm function


@dp.message_handler(lambda message: message.text)
async def result(message: types.Message):
    message.text.lower()
    url_1 = "https://zdesapteka.ru/catalog/?q=а"
    url = url_1 + message.text
    name_arr = []
    price_arr = []

    # Send a GET request to the URL
    response = se.get(url)
    # send postcode in console
    print(response)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the joke elements on the page
    jokes = soup.find_all('div', class_='content-box')

    # Extract and print the text of each joke
    for joke in jokes:
        joke_text = joke.find('a', class_='title')
        if joke_text:
            name_arr.append(joke_text.getText(strip=True))

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the joke elements on the page
    jokes = soup.find_all('div', class_='basket-box')

    # Extract and print the text of each joke
    for joke in jokes:
        joke_text = joke.find('span', class_='price_value product_current_price')
        if joke_text:
            price_arr.append(joke_text.getText(strip=True))

    analis = []

    # Output in the format "name - price"
    count = 0
    if len(name_arr) == len(price_arr):
        for i in range(len(name_arr)):
            count += 1
            analis.append(f"💊 {name_arr[i]} - {price_arr[i]}")
            if count > 29:
                break
    text_msg = "\n".join(analis)
    await bot.send_message(message.chat.id, text=f"Аналоги: \n{text_msg}")
    int_price = []
    for i in range(len(price_arr)):
        int_price.append(price_arr[i].replace(" ", ""))

    int_price2 = []

    # finding the cheapest

    for i in range(len(price_arr)):
        int_price2.append(int(int_price[i].replace("руб.", "")))

    minIndex = int_price2.index(min(int_price2))

    # sending the cheapest

    await bot.send_message(message.chat.id, text=f"Самое дешевое: 💵 {name_arr[minIndex]} - {int_price2[minIndex]} руб.")

    # pars photo url

    url_photo = f'https://yandex.ru/images/search?from=tabbar&text={message.text}'
    response_photo = se.get(url_photo)
    print(f'photo {response_photo}')
    soup = BeautifulSoup(response_photo.content, 'html.parser')
    images = soup.find_all('img', class_='serp-item__thumb justifier__thumb')
    for image in images:
        src = image.get("src")
        if src:
            print(src)

            # photo src in console

            src_compl = f'https:{src}'

            # sending photo in user chat

            await bot.send_photo(message.chat.id, photo=f'{src_compl}')

            # send photo url in console

            print(src_compl)

        # break in cycle
        break

    # advice from ChatGPT

    await bot.send_message(message.chat.id, text=f"<code>Подожди немного, ChatGPT даст вам совет🙈...</code>", parse_mode="HTML")
    engine = "text-davinci-003"
    prompt = f"Лучший аналог лекарства под названием {message.text}, обоснуй, и напиши цену аналога в рублях"
    completion = openai.Completion.create(engine=engine,
                                          prompt=prompt,
                                          temperature=0.5,
                                          max_tokens=1000)
    gpt_otv = completion.choices[0]['text']
    if gpt_otv[0] == ".":
        gpt_otv_compl = gpt_otv[3:]
        await bot.send_message(message.chat.id, text=gpt_otv_compl)
        print(True)
    else: await bot.send_message(message.chat.id, text=completion.choices[0]['text'])


if __name__ == '__main__':
    print("Let's go!")
    executor.start_polling(dp, skip_updates=True)
    print("Stop work!")
