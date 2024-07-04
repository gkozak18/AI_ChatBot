import config
from openai import OpenAI
import search


client = OpenAI()


class ChatBot:
    def __init__(self, system_prompt = "", model = "gpt-4o", temperature = 0, search=True):
        self.system_prompt = system_prompt
        if not system_prompt:
            self.system_prompt = """
            You are a smart bot assistant and you need to make some research on some topics\
            You will recive a user question and some data found in internet and you need to answer that question \
            using recived data. Don't try to answer by your own. 
                """
        self.history = [{"role": "system", "content": self.system_prompt}]
        self.model = model
        self.temperature = temperature
    
    def __call__(self, query):
        self.history.append({"role": "user", "content": query})
        found_data = self.search(query)
        self.history.append({"role": "assistant", "content": found_data})
        result = self.execute()
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = client.chat.completions.create(
            model = self.model,
            temperature = self.temperature,
            messages = self.history
        )
        return completion.choices[0].message.content
    
    def search(self, query):
        urls = search.search_urls(query)[:2]
        data = "\n".join(["url: " + url + "data: " + search.parse_url(url) for url in urls])
        #data = {url: search.parse_url(url) for url in urls}
        return data


if __name__ == "__main__":
    query = "What is in Nvidia's new Blackwell GPU?"
    bot = ChatBot()
    result = bot(query)
    print(result)
