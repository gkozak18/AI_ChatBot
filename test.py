import config 
from openai import OpenAI 


client = OpenAI()


def test1(query):
    result = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": query}]
    )
    print(result.choices[0].message.content)


if __name__ == "__main__":
    query = "What is in Nvidia's new Blackwell GPU?"
    test1(query)
