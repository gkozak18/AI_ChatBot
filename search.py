import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from pydantic import BaseModel
from openai import OpenAI
import instructor
from tavily import TavilyClient
import os


ddg = DDGS()
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


class IsSearchNeeded(BaseModel):
    result: bool = False


def search_urls(query: str, max_results=6) -> list[str]:
    results = ddg.text(query, max_results=max_results)
    return [i["href"] for i in results]

def parse_url(url: str) -> str:
    if not url:
        return "There's no url"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to retrieve the webpage."
    soup = BeautifulSoup(response.text, 'html.parser')
    data = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        text = tag.get_text(" ", strip=True)
        if text:
            data.append(text)
    data = "\n".join(data)
    return data


class Searcher:
    def __init__(self, mode="tavily", model="gpt-4o"):
        self.history = []
        self.mode = mode
        self.model = model
    
    def is_search_needed(self, query, content = ""):
        openai_client = instructor.from_openai(OpenAI())
        prompt = f"""
        You are a smart classification model and you need to clasify user question in two groups. \
        The first group is the questions which need the external data from internet, \
        for example they can be technical questions or recent news. \
        The secont group is the questions which can be answerd without external data, \
        for example question about the data that you already have or simple commands \
        like translating your previous messages or giving links which were used to your previous answer ect. \
        Please answer 'True' if the question belongs to the first class \
        and 'False' if the question belongs to the second. \n
        Here is that user question: {query} \n
        Here is the context that you have: {content}
            """
        messages = [{"role": "system", "content": prompt}]
        response = openai_client.chat.completions.create(
            model = self.model,
            response_model = IsSearchNeeded,
            temperature = 0,
            messages = messages
        )
        if response.result:
            print("Search is needed")
            return True
        else:
            print("Search is not needed")
            return False
    
    def is_search_asked(self, query):
        openai_client = instructor.from_openai(OpenAI())
        prompt = f"""
            You need to determine whether the user is asking for a search or not. \
            You get a user query and if he is asking something like 'can you search ..' etc. \
            you should answer 'True' and if not answer 'False'. \
            User's Query: {query}
        """
        messages = [{"role": "system", "content": prompt}]
        response = openai_client.chat.completions.create(
            model = self.model,
            response_model = IsSearchNeeded,
            temperature = 0,
            messages = messages
        )
        if response.result:
            print("Search is asked")
            return True
        else:
            print("Search is not asked")
            return False
    
    def search(self, query):
        result = ""
        if self.mode == "tavily":
            results = tavily_client.search(query, "basic", max_results=2, include_raw_content=True, include_answer=True)
            #print("\n", result, "\n")
            for res in results["results"]:
                result += res["content"] + "\n" + res["url"]
        return result
