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
            using recived data. Don't try to answer by your own. You also need to save links.
                """
        self.long_history = [{"role": "system", "content": self.system_prompt}]
        self.short_history = [{"role": "system", "content": self.system_prompt}]
        self.assistant_history = []
        self.model = model
        self.temperature = temperature
    
    def __call__(self, query: str, history: list[dict[str, str]] | None = None):
        assistant_message = ""
        if self.is_search_needed(query):
            found_data = self.search(query)
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
            messages = self.long_history + messages
        result = self.execute(messages)

        # short history
        self.short_history.append(user_message)
        self.short_history.append({"role": "assistant", "content": result})
        # long history
        if assistant_message:
            self.long_history.append(assistant_message)
        self.long_history.append(user_message)
        self.long_history.append({"role": "assistant", "content": result})
        # assistant history
        if assistant_message:
            self.assistant_history.append(assistant_message)
        return result
    
    def execute(self, messages: list[dict[str, str]]):
        completion = client.chat.completions.create(
            model = self.model,
            temperature = self.temperature,
            messages = messages
        )
        return completion.choices[0].message.content
    
    def search(self, query: str):
        urls = search.search_urls(query)[:2]
        data = "\n".join(["url: " + url + "data: " + search.parse_url(url) for url in urls])
        #data = {url: search.parse_url(url) for url in urls}
        return data
    
    def is_search_needed(self, query: str):
        if len(self.assistant_history) > 0:
            content = self.assistant_history[-1]["content"]
        else:
            content = ""
        prompt = f"""
        You are a smart classification model and you need to clasify user question in two groups. \
        The first group is the questions which need the external data from internet, \
        for example they can be technical questions or recent news. \
        The secont group is the questions which can be answerd without external data, \
        for example question about the data that you already have or simple commands \
        like translating your previous messages or giving links which were used to your previous answer ect. \
        Please answer 'first' if the question belongs to the first class \
        and 'second' if the question belongs to the second. \n
        Here is that user question: {query} \n
        Here is the context that you have: {content}
            """
        if len(self.assistant_history) > 0:
            messages = [{"role": "system", "content": prompt}] + [self.assistant_history[-1]]
        else:
            messages = [{"role": "system", "content": prompt}]
        result = client.chat.completions.create(
            model = self.model,
            temperature = 0,
            messages = messages
        )
        result = result.choices[0].message.content.lower()
        if "first" in result:
            print("Search is needed")
            return True
        elif "second" in result:
            print("Search is not needed")
            return False
        else:
            print("is_search_needed works incorrectly")
            print("result:", result)

