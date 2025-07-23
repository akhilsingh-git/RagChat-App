from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import pipeline, TextIteratorStreamer
from threading import Thread
from sqlalchemy.orm import Session
from . import crud
import structlog

logger = structlog.get_logger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('TaylorAI/bge-micro')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.generator_pipeline = pipeline('text-generation', model='gpt2')
        logger.info("✅ Models loaded (Bi-encoder, Cross-encoder, Generator).")

    def generate_answer_stream(self, db: Session, query: str, k: int = 3):
        """
        Generates a streamed answer using a hybrid retrieval strategy with Reciprocal Rank Fusion (RRF).
        """
        # --- Stage 1: Initial Retrieval ---
        initial_k = 25
        query_vector = self.embedding_model.encode(query)
        retrieved_docs = crud.get_top_k_documents(db, query_vector, initial_k)

        if not retrieved_docs:
            logger.warning("no_docs_found_for_query", query=query)
            yield "data: I couldn't find any relevant information to answer your question.\n\n"
            return

        # --- Stage 2: Re-ranking ---
        rerank_pairs = [[query, doc.text_content] for doc in retrieved_docs]
        rerank_scores = self.reranker.predict(rerank_pairs)
        
        # --- Stage 3: Reciprocal Rank Fusion (RRF) ---
        fused_scores = {}
        k_rrf = 60 

        initial_ranks = {doc.id: rank + 1 for rank, doc in enumerate(retrieved_docs)}
        reranked_docs = sorted(zip(retrieved_docs, rerank_scores), key=lambda x: x[1], reverse=True)
        reranked_ranks = {doc.id: rank + 1 for rank, (doc, score) in enumerate(reranked_docs)}

        for doc_id, rank in initial_ranks.items():
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k_rrf + rank)
        
        for doc_id, rank in reranked_ranks.items():
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k_rrf + rank)

        sorted_fused_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        doc_map = {doc.id: doc for doc in retrieved_docs}
        final_docs = [doc_map[doc_id] for doc_id, score in sorted_fused_docs[:k]]
        
        logger.info(
            "fusion_ranking_complete", 
            initial_retrieval_count=len(retrieved_docs),
            final_selection_count=len(final_docs)
        )

        # --- Stage 4: Generation with Structured Prompt ---
        # This is the new, improved prompting strategy.
        # Instead of one long string, we format the context clearly.
        context_parts = []
        for i, doc in enumerate(final_docs):
            context_parts.append(f"Document {i+1}: {doc.text_content}")
        
        structured_context = "\n---\n".join(context_parts)

        prompt = (
            "You are a helpful AI assistant. Synthesize an answer to the following question "
            "based *only* on the provided documents. Do not use any outside knowledge.\n\n"
            f"--- CONTEXT DOCUMENTS ---\n{structured_context}\n\n"
            f"--- QUESTION ---\n{query}\n\n"
            "--- ANSWER ---\n"
        )
        
        streamer = TextIteratorStreamer(self.generator_pipeline.tokenizer, skip_prompt=True, skip_special_tokens=True)

        thread = Thread(
            target=self.generator_pipeline,
            args=(prompt,),
            kwargs={"streamer": streamer, "max_new_tokens": 150}
        )
        thread.start()

        for token in streamer:
            yield f"data: {token}\n\n"

rag_service = RAGService()

def get_rag_service():
    return rag_service