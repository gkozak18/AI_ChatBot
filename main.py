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
        self.long_history = [{"role": "system", "content": self.system_prompt}]
        self.short_history = [{"role": "system", "content": self.system_prompt}]
        self.assistant_history = []
        self.model = model
        self.temperature = temperature
    
    def __call__(self, query):
        assistant_message = ""
        if self.is_search_needed(query):
            found_data = self.search(query)
            assistant_message = {"role": "assistant", "content": found_data}
        user_message = {"role": "user", "content": query}
        if assistant_message:
            messages = self.long_history + [assistant_message] + [user_message]
        else:
            messages = self.long_history + [user_message]
        result = self.execute(messages)
        # short history
        self.short_history.append(user_message)
        self.short_history.append({"role": "assistant", "content": result})
        # long history
        if assistant_message:
            self.long_history.append({"role": "assistant", "content": assistant_message})
        self.long_history.append(user_message)
        self.long_history.append({"role": "assistant", "content": result})
        # assistant history
        if assistant_message:
            self.assistant_history.append({"role": "assistant", "content": assistant_message})
        return result
    
    def execute(self, messages):
        completion = client.chat.completions.create(
            model = self.model,
            temperature = self.temperature,
            messages = messages
        )
        return completion.choices[0].message.content
    
    def search(self, query):
        urls = search.search_urls(query)[:2]
        data = "\n".join(["url: " + url + "data: " + search.parse_url(url) for url in urls])
        #data = {url: search.parse_url(url) for url in urls}
        return data
    
    def is_search_needed(self, query):
        prompt = f"""
        You have a user question and the user-bot chat history and you need to decide\
        whether i need to search some information for you to answer teh question \
        or chat history will be enough. Answer just yes if search is needed or no if not. \
        Please never answer the question, just answer yes or no. Your task is to decide \
        whether additional search is needed or not.
        User Question: {query}
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
        if result == "yes":
            print("Search is needed")
            return True
        elif result == "no":
            print("Search is not needed")
            return False
        else:
            print("is_search_needed works incorrectly")
            print("result:", result)


def loop():
    bot = ChatBot()
    while True:
        query = input("Input your Question('exit' for exiting): ")
        if query == "exit":
            print(bot.history)
            break
        result = bot(query)
        print(result)


if __name__ == "__main__":
    #query = "What is in Nvidia's new Blackwell GPU?"
    #bot = ChatBot()
    #result = bot(query)
    #print(result)
    loop()
