import streamlit as st
import openai

import os
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def get_joke_explanation(joke):
    # This function sends the joke to OpenAI's GPT-4 and gets the response
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Explain this joke: {joke}",
                }
            ],
        )
        explanation = response.choices[0].message.content
        return explanation
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app layout
st.title("Joke Explainer")

# Text box for user input
joke = st.text_area("Enter your joke here:")

# Submit button
if st.button("Submit"):
    if joke:
        explanation = get_joke_explanation(joke)
        st.subheader("Explanation:")
        st.write(explanation)
    else:
        st.error("Please enter a joke.")