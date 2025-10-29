"""
Vector database operations using ChromaDB
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from config.settings import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """ChromaDB vector database manager"""
    
    def __init__(self):
        self.client = None
        self.embedding_model = None
        self.collections = {}
        
    def initialize(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Create default collections
            self._create_default_collections()
            
            logger.info("Vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            raise
    
    def _create_default_collections(self):
        """Create default collections for different document types"""
        collection_configs = {
            "sec_filings": {
                "name": "sec_filings",
                "metadata": {"hnsw:space": "cosine"},
                "description": "SEC filing documents and excerpts"
            },
            "news_articles": {
                "name": "news_articles", 
                "metadata": {"hnsw:space": "cosine"},
                "description": "Financial news articles"
            },
            "financial_statements": {
                "name": "financial_statements",
                "metadata": {"hnsw:space": "cosine"},
                "description": "Financial statement line items and narratives"
            },
            "research_reports": {
                "name": "research_reports",
                "metadata": {"hnsw:space": "cosine"},
                "description": "Analyst research reports and insights"
            }
        }
        
        for config in collection_configs.values():
            try:
                collection = self.client.get_or_create_collection(
                    name=config["name"],
                    metadata=config["metadata"]
                )
                self.collections[config["name"]] = collection
                logger.info(f"Collection '{config['name']}' ready")
                
            except Exception as e:
                logger.error(f"Failed to create collection '{config['name']}': {str(e)}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def add_sec_filing(self, filing_id: int, company_cik: str, form_type: str,
                       content_chunks: List[str], filing_date: str, 
                       accession_number: str) -> bool:
        """Add SEC filing content to vector database"""
        try:
            collection = self.collections["sec_filings"]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(content_chunks)
            
            # Prepare documents
            ids = [f"filing_{filing_id}_chunk_{i}" for i in range(len(content_chunks))]
            
            metadatas = []
            for i, chunk in enumerate(content_chunks):
                metadata = {
                    "filing_id": filing_id,
                    "company_cik": company_cik,
                    "form_type": form_type,
                    "filing_date": filing_date,
                    "accession_number": accession_number,
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "document_type": "sec_filing",
                    "created_at": datetime.utcnow().isoformat()
                }
                metadatas.append(metadata)
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=content_chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added SEC filing {accession_number} with {len(content_chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add SEC filing to vector DB: {str(e)}")
            return False
    
    def add_news_article(self, article_id: int, title: str, content: str,
                        company_ciks: List[str], published_at: str, 
                        source: str, sentiment: str = "neutral") -> bool:
        """Add news article to vector database"""
        try:
            collection = self.collections["news_articles"]
            
            # Combine title and content
            full_text = f"{title}\n\n{content}"
            
            # Split into chunks if content is too long
            max_chunk_size = 1000  # characters
            chunks = []
            
            if len(full_text) <= max_chunk_size:
                chunks = [full_text]
            else:
                # Split by paragraphs and combine into chunks
                paragraphs = full_text.split('\n\n')
                current_chunk = ""
                
                for paragraph in paragraphs:
                    if len(current_chunk) + len(paragraph) <= max_chunk_size:
                        current_chunk += paragraph + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = paragraph + "\n\n"
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Prepare documents
            ids = [f"news_{article_id}_chunk_{i}" for i in range(len(chunks))]
            
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "article_id": article_id,
                    "title": title,
                    "company_ciks": json.dumps(company_ciks),
                    "published_at": published_at,
                    "source": source,
                    "sentiment": sentiment,
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "document_type": "news_article",
                    "created_at": datetime.utcnow().isoformat()
                }
                metadatas.append(metadata)
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added news article {article_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add news article to vector DB: {str(e)}")
            return False
    
    def add_financial_statement(self, fs_id: int, company_cik: str, 
                               statement_type: str, line_items: Dict[str, Any],
                               period_end: str) -> bool:
        """Add financial statement data to vector database"""
        try:
            collection = self.collections["financial_statements"]
            
            # Create text representations of financial data
            texts = []
            metadatas = []
            
            for line_item, value in line_items.items():
                # Create natural language representation
                text = f"{statement_type}: {line_item} - {value} for period ending {period_end}"
                texts.append(text)
                
                metadata = {
                    "fs_id": fs_id,
                    "company_cik": company_cik,
                    "statement_type": statement_type,
                    "line_item": line_item,
                    "value": str(value),
                    "period_end": period_end,
                    "document_type": "financial_statement",
                    "created_at": datetime.utcnow().isoformat()
                }
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Prepare IDs
            ids = [f"fs_{fs_id}_{i}" for i in range(len(texts))]
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added financial statement {fs_id} with {len(texts)} line items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add financial statement to vector DB: {str(e)}")
            return False
    
    def search_similar(self, query: str, collection_name: str = None, 
                      n_results: int = 10, where_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Use all collections if none specified
            collections_to_search = []
            if collection_name:
                if collection_name in self.collections:
                    collections_to_search = [self.collections[collection_name]]
                else:
                    logger.error(f"Collection '{collection_name}' not found")
                    return []
            else:
                collections_to_search = list(self.collections.values())
            
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            all_results = []
            
            for collection in collections_to_search:
                try:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results,
                        where=where_filter,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    # Format results
                    for i in range(len(results["documents"][0])):
                        result = {
                            "document": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i],
                            "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                            "collection": collection.name
                        }
                        all_results.append(result)
                
                except Exception as e:
                    logger.error(f"Error searching collection {collection.name}: {str(e)}")
                    continue
            
            # Sort by similarity and return top results
            all_results.sort(key=lambda x: x["similarity"], reverse=True)
            return all_results[:n_results]
            
        except Exception as e:
            logger.error(f"Failed to search vector database: {str(e)}")
            return []
    
    def search_by_company(self, query: str, company_cik: str, 
                         n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for documents related to a specific company"""
        where_filter = {"company_cik": company_cik}
        return self.search_similar(query, where_filter=where_filter, n_results=n_results)
    
    def search_by_date_range(self, query: str, start_date: str, end_date: str,
                           n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for documents within a date range"""
        # Note: ChromaDB filtering is limited, this is a simplified approach
        results = self.search_similar(query, n_results=n_results * 2)  # Get more to filter
        
        filtered_results = []
        for result in results:
            metadata = result["metadata"]
            
            # Check different date fields
            doc_date = None
            if "filing_date" in metadata:
                doc_date = metadata["filing_date"]
            elif "published_at" in metadata:
                doc_date = metadata["published_at"].split("T")[0]  # Extract date part
            elif "period_end" in metadata:
                doc_date = metadata["period_end"]
            
            if doc_date and start_date <= doc_date <= end_date:
                filtered_results.append(result)
                
            if len(filtered_results) >= n_results:
                break
        
        return filtered_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        stats = {}
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = {
                    "document_count": count,
                    "name": name
                }
            except Exception as e:
                logger.error(f"Failed to get stats for collection {name}: {str(e)}")
                stats[name] = {"error": str(e)}
        
        return stats
    
    def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete specific documents from a collection"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            collection = self.collections[collection_name]
            collection.delete(ids=document_ids)
            
            logger.info(f"Deleted {len(document_ids)} documents from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return False
    
    def reset_collection(self, collection_name: str) -> bool:
        """Reset a collection (delete all documents)"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection '{collection_name}' not found")
                return False
            
            self.client.delete_collection(collection_name)
            
            # Recreate the collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.collections[collection_name] = collection
            
            logger.info(f"Reset collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {str(e)}")
            return False
    
    def close(self):
        """Close vector database connections"""
        try:
            # ChromaDB doesn't require explicit closing
            logger.info("Vector database connections closed")
        except Exception as e:
            logger.error(f"Error closing vector database: {str(e)}")


# Global vector database instance
vector_db = VectorDatabase()


def init_vector_database():
    """Initialize the global vector database instance"""
    vector_db.initialize()


def get_vector_db() -> VectorDatabase:
    """Get the global vector database instance"""
    if not vector_db.client:
        init_vector_database()
    return vector_db