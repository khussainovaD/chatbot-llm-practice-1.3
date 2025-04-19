import streamlit as st
import pymongo
from pymongo import MongoClient
import os
import ollama


mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["constitution_db"]
collection = db["articles"]

st.title("Constitution AI Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def get_response(prompt, context):
    try:
        client = ollama.Client()
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        response = client.generate(model="llama3.2:1b", prompt=full_prompt)
        return response["response"]
    except Exception as e:
        return f"Error generating response: {e}"

def generate_embedding(text):
    """Mock function for embedding generation."""
    return [0.1] * 2048

def load_constitution_to_mongo(filename):
    """Load and process the constitution text into MongoDB as articles."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()

        articles = content.split("Article")[1:]  
        for i, article in enumerate(articles):
            article_text = f"Article {article.strip()}"
            embedding = generate_embedding(article_text)

            collection.insert_one({
                "id": f"article_{i+1}",
                "text": article_text,
                "embedding": embedding
            })

        st.success("Constitution loaded and processed successfully into MongoDB!")
    except Exception as e:
        st.error(f"Failed to load constitution: {e}")

def search_articles(query):
    """Search MongoDB for relevant articles based on query."""
    query_embedding = generate_embedding(query)
    articles = collection.find()
    results = []

    for article in articles:
        article_embedding = article.get("embedding", [])
        similarity = 1 - sum((qe - ae) ** 2 for qe, ae in zip(query_embedding, article_embedding))
        results.append((similarity, article))

    results.sort(reverse=True, key=lambda x: x[0])
    return [result[1] for result in results[:5]]

constitution_path = "constitution.txt"
if os.path.exists(constitution_path):
    if collection.count_documents({}) == 0:
        load_constitution_to_mongo(constitution_path)

st.sidebar.subheader("Search Constitution")
search_query = st.sidebar.text_input("Search in Constitution")
if st.sidebar.button("Search"):
    if search_query.strip():
        try:
            results = search_articles(search_query)
            st.sidebar.write("Search Results:")
            for article in results:
                st.sidebar.markdown(f"- {article['text'][:200]}...")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

st.subheader("Chat with AI")
with st.container():
    user_input = st.text_input("Ask a question about the Constitution:")

    if st.button("Send"):
        if user_input.strip():
            st.session_state["messages"].append({"user": "You", "content": user_input})
            try:
                results = search_articles(user_input)
                relevant_context = "\n\n".join(article['text'] for article in results)
                bot_response = get_response(user_input, relevant_context)

                st.session_state["messages"].append({"user": "Bot", "content": bot_response})
            except Exception as e:
                st.error(f"Error: {e}")

    for message in st.session_state["messages"]:
        if message["user"] == "You":
            st.markdown(f"<div style='text-align: left; padding: 8px; background-color: #d9fdd3; border-radius: 10px; margin: 5px 0;'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left; padding: 8px; background-color: #f0f0f0; border-radius: 10px; margin: 5px 0;'>{message['content']}</div>", unsafe_allow_html=True)
