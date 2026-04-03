import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for embeddings using FAISS or similar"""
    
    def __init__(self, dimension=384, use_faiss=True):
        self.dimension = dimension
        self.use_faiss = use_faiss
        self.embeddings_file = 'embeddings.json'
        self.index_file = 'faiss_index.bin'
        self.model = None  # Lazy-load on first use
        
        if use_faiss:
            self.index = faiss.IndexFlatL2(dimension)
            self.documents = []
        else:
            self.embeddings_dict = {}
        
        self._load_if_exists()
    
    def _get_model(self):
        """Lazy-load the sentence transformer model"""
        if self.model is None:
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully")
        return self.model
    
    def _load_if_exists(self):
        """Load existing embeddings from disk"""
        try:
            if self.use_faiss and os.path.exists(self.index_file):
                self.index = faiss.read_index(self.index_file)
                logger.info("Loaded FAISS index from disk")
            
            if os.path.exists(self.embeddings_file):
                with open(self.embeddings_file, 'r') as f:
                    data = json.load(f)
                    if self.use_faiss:
                        self.documents = data.get('documents', [])
                    else:
                        self.embeddings_dict = data.get('embeddings', {})
                logger.info("Loaded embeddings from disk")
        except Exception as e:
            logger.warning(f"Could not load existing embeddings: {e}")
    
    def add_document(self, document_id, text, metadata=None):
        """Add document and compute embeddings"""
        try:
            embedding = self._get_model().encode(text)
            embedding = np.array([embedding]).astype('float32')
            
            if self.use_faiss:
                self.index.add(embedding)
                self.documents.append({
                    'id': str(document_id),
                    'text': text[:1000],  # Store first 1000 chars
                    'metadata': metadata or {}
                })
            else:
                self.embeddings_dict[str(document_id)] = {
                    'embedding': embedding[0].tolist(),
                    'text': text[:1000],
                    'metadata': metadata or {}
                }
            
            return True
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return False
    
    def search(self, query_text, top_k=5):
        """Search for similar documents"""
        try:
            query_embedding = self._get_model().encode(query_text)
            query_embedding = np.array([query_embedding]).astype('float32')
            
            if self.use_faiss:
                distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
                results = []
                for idx, distance in zip(indices[0], distances[0]):
                    if idx < len(self.documents):
                        results.append({
                            'id': self.documents[idx]['id'],
                            'text': self.documents[idx]['text'],
                            'metadata': self.documents[idx]['metadata'],
                            'similarity': float(1 / (1 + distance))
                        })
                return results
            else:
                # Simple search using dict
                results = []
                for doc_id, doc_data in self.embeddings_dict.items():
                    doc_embedding = np.array(doc_data['embedding']).astype('float32')
                    similarity = np.dot(query_embedding[0], doc_embedding) / (
                        np.linalg.norm(query_embedding[0]) * np.linalg.norm(doc_embedding)
                    )
                    results.append({
                        'id': doc_id,
                        'text': doc_data['text'],
                        'metadata': doc_data['metadata'],
                        'similarity': float(similarity)
                    })
                
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:top_k]
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def save(self):
        """Persist vector store to disk"""
        try:
            if self.use_faiss:
                faiss.write_index(self.index, self.index_file)
                with open(self.embeddings_file, 'w') as f:
                    json.dump({'documents': self.documents}, f)
            else:
                with open(self.embeddings_file, 'w') as f:
                    json.dump({'embeddings': self.embeddings_dict}, f)
            
            logger.info("Vector store saved to disk")
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def delete_document(self, document_id):
        """Delete document from vector store"""
        if self.use_faiss:
            self.documents = [d for d in self.documents if d['id'] != str(document_id)]
        else:
            if str(document_id) in self.embeddings_dict:
                del self.embeddings_dict[str(document_id)]
        
        return True
    
    def clear(self):
        """Clear all embeddings"""
        if self.use_faiss:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
        else:
            self.embeddings_dict = {}

# Global vector store instance
vector_store = VectorStore(
    dimension=Config.VECTOR_DIM,
    use_faiss=Config.USE_FAISS
)
