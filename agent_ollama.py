from search import search_urls, parse_url
from langchain_community.llms import Ollama


class OllamaAgent:
    def __init__(self, model="mistral"):
        self.llm = Ollama(
            model = model
        )
        self.system_prompt = """"
            You are a smart ai assistant which can answer the users question \
            using searched data if available.
        """
        self.history = [{"role": "system", "content": self.system_prompt}]
    
    def __call__(self, query):
        if self.is_search_needed(query):
            search_results = self.search_data(query)
            self.history.append({"role": "searcher", "content": search_results})
        self.history.append({"role": "user", "content": query})
        history = self.str_history(self.history)
        result = self.llm.invoke(history)
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def str_history(self, history):
        result = ""
        for item in history:
            result += item["role"] + ": " + item["content"] + "\n"
        return result
    
    def search_data(self, query):
        urls = search_urls(query)[:2]
        data = ""
        for url in urls:
            data += parse_url(urls[0]) + "/n"
        return data
    
    def is_search_needed(self, query: str):
        if len(self.history) > 0:
            content = self.history
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
        result = self.llm(prompt)
        if "first" in result.lower():
            print("Search is needed")
            return True
        elif "second" in result.lower():
            print("Search is not needed")
            return False
        else:
            print("is_search_needed works incorrectly")
            print("result:", result)
