from agent import ChatBot
from agent_ollama import OllamaAgent


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
