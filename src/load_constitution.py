from pymongo import MongoClient
import ollama
import pickle

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["constitution_db"]
collection = db["constitution_embeddings"]

def generate_embedding(text):
    client = ollama.Client()
    response = client.embeddings(model="llama3.2:1b", prompt=text)
    return response['embedding']

def load_constitution(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()

        sections = content.split("}")
        for i, section in enumerate(sections):
            section = section.strip()
            if section and "{" in section:
                section_text = section.replace("{", "").strip()
                embedding = generate_embedding(section_text)
                document = {
                    "id": f"section_{i+1}",
                    "text": section_text,
                    "embedding": pickle.dumps(embedding),
                }
                collection.insert_one(document)
                print(f"Section {i+1} added.")
        print("Constitution successfully loaded!")
    except Exception as e:
        print(f"Error: {e}")

constitution_path = "constitution.txt"
load_constitution(constitution_path)
