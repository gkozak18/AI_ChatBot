from agent import ChatBot


def loop():
    bot = ChatBot()
    while True:
        query = input("Input your Question('exit' for exiting): ")
        if query == "exit":
            print(bot.short_history)
            break
        result = bot(query)
        print(result)


if __name__ == "__main__":
    #query = "What is in Nvidia's new Blackwell GPU?"
    #bot = ChatBot()
    #result = bot(query)
    #print(result)
    loop()
