# Vectors
(I know most of these things, I have read these during my coursework, CNNs,differnet distances, the layers, how feature matrix, filter etc etc works so here I have only mentioned key points to recall concepts.)
Vector- Machines don't understand Hi or hello lke humans do so these are converted into numbers(matrix) also called as feature matrix. This numerical representation helps to understand the semantic menaing better by the machine.
Vectors are converted from textor images etc using embeddings.
Embeddings- vector rep of data.
If two pieces are similar, their vectors will be close.
## VECTOR SIMILARITY
Cosine similarity- angle between vectors, the closer to 1, higher match, the closer to -1, the different they are.
Vector similariyt can be found using- cosine, euclidean, dot product.
## Vector index
to search through vectors, an index is maintained for fast lookup. Some examples- 
* HNSW (Hierarchical Navigable Small World) – popular for large-scale search

* FAISS (Facebook AI Similarity Search) – library that builds efficient indexes

## Vector databases
1. Stores vectors, metadata, supports similarity search
2. allows filtering
## vectors in RAG
LLM doesn’t know all facts → so:
Convert documents into embeddings
Store them in a vector database
At query time, retrieve relevant info using vector search
Pass it to the LLM (like GPT-4)