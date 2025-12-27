import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.document_loader import load_and_split_pdf
from src.vector_store import create_vector_store
from src.rag import create_rag_chain
from langchain_core.documents import Document

class TestBackend(unittest.TestCase):

    @patch("src.document_loader.PyMuPDFLoader")
    def test_load_and_split_pdf(self, MockLoader):
        # Mock loader behavior
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.load.return_value = [Document(page_content="Test content")]
        
        # Call function
        chunks = load_and_split_pdf("dummy.pdf")
        
        # Verify
        self.assertTrue(len(chunks) > 0)
        self.assertIsInstance(chunks[0], Document)
        print("test_load_and_split_pdf passed!")

    @patch("src.vector_store.FAISS")
    def test_create_vector_store(self, MockFAISS):
        # Mock inputs
        chunks = [Document(page_content="Test chunk")]
        mock_embedding = MagicMock()
        
        # Call function
        create_vector_store(chunks, mock_embedding)
        
        # Verify FAISS.from_documents was called
        MockFAISS.from_documents.assert_called_once()
        print("test_create_vector_store passed!")

    def test_rag_chain_creation(self):
        # Mock inputs
        mock_vector_store = MagicMock()
        mock_llm = MagicMock()
        
        # Call function
        chain = create_rag_chain(mock_vector_store, mock_llm)
        
        # Verify chain is created (it returns an object)
        self.assertIsNotNone(chain)
        print("test_rag_chain_creation passed!")

if __name__ == "__main__":
    unittest.main()
