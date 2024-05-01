import csv
import textwrap
import warnings
import google.generativeai as genai
from IPython.display import Markdown
import pandas as pd

warnings.filterwarnings("ignore")

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def configure_generative_ai(api_key):
    genai.configure(api_key=api_key)

def generate_answer(question):
    model = genai.GenerativeModel(model_name='gemini-pro')
    response = model.generate_content(question)
    answer = response.text
    return answer


csv_file = input("Enter CSV File: ")
df = pd.read_csv(csv_file)


def main(csv_file):
    while True:
        question = input("\nAsk a question about this data: ")
        if(question == "exit"):
            break
        else:
            answer = generate_answer("I have a dataset in pandas, containing rows [ID,Date,Month,Year,Day,Time,Log Level,Message,Side,IP Address]. Based on my following question, generate a python line that i can use with exec to query the dataset. Make sure that you dont add any other text, hence what you give will be executed autmatically. My Question: "+question)
            print("Answer:")
            try:
                exec(f"tempres = {answer}\nprint(tempres)")
            except:
                print("Gemini had some problem executing the command, please try again")

if __name__ == "__main__":
    api_key = "GEMINI API KEY"  # Replace with your Gemini API key
    configure_generative_ai(api_key)
    # Update with your CSV file path
    main(csv_file)

