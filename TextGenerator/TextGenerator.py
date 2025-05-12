import os
import json
import asyncio
import aiohttp
import logging
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)  # логгер

class TextGenerator:


    def __init__(self):
        self.api_key = os.getenv('GEMINI_API')
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.logger = logging.getLogger(__name__)  # Логгер
        self.proxies = "socks5://localhost:1080"
        self.config_path = 'proxy_config.json'

        if not self.api_key:
            self.logger.error("GEMINI_API not found in environment variables")
            raise ValueError("GEMINI_API environment variable is required")

        self.logger.info("GeminiLetterAnalyzer initialized")


    #start proxy
    async def start_xray_proxy(self):
        self.logger.info("Starting Xray proxy...")
        try:
            process = await asyncio.create_subprocess_exec(
                "xray", "run", "-c", self.config_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if process.returncode is not None:
                stderr = await process.stderr.read()
                self.logger.error(f"Xray failed to start: {stderr.decode()}")
                raise RuntimeError(f"Xray failed to start: {stderr.decode()}")

            self.logger.info("Xray proxy started successfully")
            return process

        except Exception as e:
            self.logger.error(f'Error starting Xray proxy: {str(e)}')
            raise


    #base prompt creation
    def _create_prompt(self, letter_text):
        self.logger.debug("Creating prompt for letter analysis")
        return f'''Выдай ответ в формате json. Я отправлю тебе текст письма солдата. Любое письмо принадлежит периоду 
        Великой Отечественной войны. Описание должно соответствовать тому периоду времени. 
        Первым ключом json сделай ключ "sex", в котором должна быть 1, если письмо писала женщина и 0, если мужчина. 
        Далее разбей письмо на несколько кадров. Для каждого кадра составь подробный промпт для генерации в нейросети 
        Kandinsky. Эти кадры запиши в ключ "cadres" в виде списка. 
        Далее проанализируй исходный текст письма: в трудных словах, НЕ во всех, расставь ударения, добавив символ "+" 
        перед гласной, на которую оно падает. Расставь акценты, пометив нужные слова звездочками: **слово**.
        Формат вывода: сначала пол, затем кадры, затем отредактированный текст:
            "sex": 0 или 1,
            "frames": ["список", "кадров"],
            "original_text": "текст с **разметкой**"
        Текст письма: {letter_text}'''


    #parser
    def _parse_response(self, response_data):
        try:
            self.logger.debug("Parsing API response")
            response_text = response_data['candidates'][0]['content']['parts'][0]['text']
            self.logger.debug(f"Response text: {response_text[:50]}...")

            clear_text = response_text.strip('` \n json')
            self.logger.debug(f"Cleared text: {clear_text[:50]}...")

            parsed = json.loads(clear_text)

            if not all(key in parsed for key in ['sex', 'frames', 'original_text']):
                self.logger.warning("Parsed response misses required fields")

            self.logger.debug("Response parsed successfully")
            return dict(parsed.items())

        except Exception as e:
            self.logger.error(f'Error parsing response: {str(e)}')

        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Error parsing API response: {str(e)}", exc_info=True)
            raise ValueError("Invalid API response format") from e


    #prompt analyzer
    async def analyze_letter(self, letter_text):
        try:
            self.logger.info(f"Starting analysis for letter: {letter_text[:50]}...")
            prompt = self._create_prompt(letter_text)
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }

            self.logger.debug("Sending request to Gemini API")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    params={"key": self.api_key},
                    proxy=self.proxies,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        self.logger.error(f"API request failed. Status: {response.status}. Error: {error_text[:200]}..")
                        return None

                    response_data = await response.json()
                    self.logger.debug("Successfully received response from API")

                    result = self._parse_response(response_data)
                    self.logger.info("Letter analysis completed successfully")
                    return result

        except asyncio.TimeoutError:
            self.logger.warning("Request to Gemini API timed out after 10 seconds")
            return None
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error during API request: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error during API request: {str(e)}", exc_info=True)
            return None


async def main():
    analyzer = TextGenerator()
    await analyzer.start_xray_proxy()

    letter_text = '''Здравствуйте, мои дорогие мама, бабушка, Нина, Юра, Ольга. Шлю вам горячий привет и желаю самых лучших успехов в 
    вашей жизни. Мама, это письмо пишу перед боем. Через полтора часа иду в бой, вернусь или нет, не знаю, поэтому решил написать. 
    Может быть, это письмо последнее. А вот жить хочется, хочется дышать, хочется посмотреть на вас хотя бы одним глазом. 
    Сегодня вступил в ряды ВКП(Б) и пойду в бой коммунистом, и если погибну, то считайте, что был коммунист. 
    До рассвета осталось совсем немного времени, и вот в голову залазят всякие мысли. И жить хочется, ведь вы сами знаете, 
    как я провел свою юность, остальное время… и все же жить хочется. Но жить под ярмом немцев не хочу, так лучше погибнуть. 
    Писать больше времени нет. До свидания, дорогие родители! Крепко, крепко целую руки, 24 января 1943 года'''

    result = await analyzer.analyze_letter(letter_text)
    if result:
        pprint(result)
    else:
        print("Failed to analyze the letter")


if __name__ == "__main__":
    asyncio.run(main())