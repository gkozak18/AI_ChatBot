import config
from openai import OpenAI
from search import Searcher
from pydantic import BaseModel


client = OpenAI()


class ChatBot:
    def __init__(self, system_prompt = "", model = "gpt-4o", temperature = 0, search=True):
        self.system_prompt = system_prompt
        if not system_prompt:
            self.system_prompt = """
            You are a smart bot assistant and you need to make some research on some topics\
            You will recive a user question and some data found in internet and you need to answer that question \
            using recived data. Don't try to answer by your own. You also need to save links.
                """
        self.history = [{"role": "system", "content": self.system_prompt}]
        self.model = model
        self.searcher = Searcher()
        self.temperature = temperature
    
    def __call__(self, query: str, history: list[dict[str, str]] | None = None):
        assistant_message = ""
        if self.searcher.is_search_asked(query):
            found_data = self.searcher.search(query)
            assistant_message = {"role": "assistant", "content": found_data}
        user_message = {"role": "user", "content": query}

        # creating messages for gpt
        if assistant_message:
            messages = [assistant_message] + [user_message]
        else:
            messages = [user_message]
        
        # external history or internal
        if history:
            messages = history + messages 
        else:
            messages = self.history + messages
        result = self.execute(messages)

        # history
        if assistant_message:
            self.history.append(assistant_message)
        self.history.append(user_message)
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def execute(self, messages: list[dict[str, str]]):
        completion = client.chat.completions.create(
            model = self.model,
            temperature = self.temperature,
            messages = messages
        )
        return completion.choices[0].message.content

