import sys
import os
import unittest
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import generate_embedding, collection


class TestLlamaChatbot(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

    def tearDown(self):
        """Cleanup after each test"""
        if os.path.exists("mock_file.txt"):
            os.remove("mock_file.txt")

    def test_generate_embedding(self):
        """Test embedding generation"""
        sample_text = "Sample embedding test text."
        embedding = generate_embedding(sample_text)

        self.assertIsInstance(embedding, list, "Embedding is not a list")
        self.assertEqual(len(embedding), 2048, "Embedding size is not correct")

    def test_mongo_collection(self):
        """Test MongoDB collection insertion and retrieval"""
        test_document = {
            "id": "test_article",
            "text": "This is a test article.",
            "embedding": [0.1] * 2048
        }

        collection.insert_one(test_document)
        result = collection.find_one({"id": "test_article"})

        self.assertIsNotNone(result, "Document not found in the collection")
        self.assertEqual(result["text"], test_document["text"], "Text does not match")
        self.assertEqual(result["embedding"], test_document["embedding"], "Embedding does not match")

        # Clean up
        collection.delete_one({"id": "test_article"})


if __name__ == "__main__":
    unittest.main()
