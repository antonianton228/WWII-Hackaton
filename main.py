import asyncio
import time

from ImageGen.StaticImageGenerator import StaticImageGenerator
from SpeechGenerator.SpeechGenerator import SpeechGenerator


async def main():
    ## Здесь кусок кода, который генерит текст, на выходе получим следующий словарь
    genemi_result = {
        "sex": 1,
        "cadres": [
            "Солдат готовится к бою",
            "Солдат пишет пиьмо",
            "Солдаты воюют",
            "СССР победило германию"
        ],
        "original_text": '''Здравствуйте, мои дорогие мама, бабушка, Нина, Юра, Ольга. Шлю вам горячий привет и желаю самых лучших успехов в вашей жизни. Мама, это письмо пишу перед боем. Через полтора часа иду в бой, вернусь или нет, не знаю, поэтому решил написать. Может быть, это письмо последнее. А вот жить хочется, хочется дышать, хочется посмотреть на вас хотя бы одним глазом. Сегодня вступил в ряды ВКП(Б) и пойду в бой коммунистом, и если погибну, то считайте, что был коммунист. До рассвета осталось совсем немного времени, и вот в голову залазят всякие мысли. И жить хочется, ведь вы сами знаете, как я провел свою юность, остальное время… и все же жить хочется. Но жить под ярмом немцев не хочу, так лучше погибнуть. Писать больше времени нет. До свидания, дорогие родители! Крепко, крепко целую руки, 24 января 1943 года'''
    }

    ## Тут второй метод (в FastApi) для генерации картинок
    image_generator = StaticImageGenerator()
    for prompt in genemi_result["cadres"]:
        image_generator.add_prompt(prompt)
    await image_generator.start_image_generations()
    ## Тут мы заканчиваем метод, после этого раз в какое-то время фронт будет стучаться и справшивать, готова ли генерация. Тут симуляция этого стука))
    for i in range(100):
        status = await image_generator.is_generation_ready()
        print(status)
        if status:
            break
        time.sleep(2)
    ## Представим, что достучались, фронт об этом узнал и показывает картинки, метод закончен
    for img in image_generator.get_image_list():
        img.show()


    ## теперь голос
    voice_generator = SpeechGenerator(genemi_result["original_text"], genemi_result["sex"])
    voice_bytes = voice_generator.generate_voice()
    # Дальше только монтаж, для примера сохраню голос в файл (на бэке этого не будет)
    with open("voice.mp3", "wb") as f:
        f.write(voice_bytes)



if __name__ == "__main__":
    asyncio.run(main())