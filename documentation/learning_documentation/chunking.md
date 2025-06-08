# Chunking strategies
- breaking large texts into smaller meaniningful segments before embedding them into vectors. This directly affects the relevance, accuracy and efficiency of LLM- based applications.
- too large chunks- noise, dilution, less precise results.
- too small- lose context, miss connections.
- Mixing small and large chunks = inconsistency in embedding granularity.

1. Fixed-Size Chunking - Break text into chunks of N tokens/characters regardless of content.
2. Sentence-Based Chunking- Split by sentence using NLP libraries like nltk, spacy, then group a few sentences per chunk.
3. Sliding Window Chunking- Overlap between chunks using a "sliding window" to preserve context across chunks.
4.  Recursive Text Splitter (LangChain)- Tries to split based on larger semantic units first (like paragraphs), then falls back to sentences, then tokens.
5.   Markdown / Semantic Section-Based Chunking-  Chunk based on markdown headers, code blocks, or topics.



| Use Case               | Best Strategy                    |
| ---------------------- | -------------------------------- |
| PDFs or reports        | Recursive / Markdown-based       |
| Semantic search        | Sentence-based or Sliding window |
| Chatbot context memory | Sliding window with overlaps     |
| Fast proof of concept  | Fixed-size chunking              |
| Mixed-length documents | Recursive splitter               |
