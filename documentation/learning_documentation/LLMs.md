#Summary of understanding
Resource 1:https://www.pinecone.io/learn/llm-ecosystem/
## LLMs
1. Powerful for autocomplete tasks.
2. Alone are black boxes, prone to hallucinations, can not access real time data, no memory across sessions.
3. LLMs alone operate on parametric knowledge. That is, knowledge stored within the model parameters, which the model encodes during model training.
4. Hosted LLMs- 
   1. Run by companies
   2. no setuo rqd-API call
   3. expensive at scale
   4. can't control the data or model
   5. privacy and data security concerns
5. Local LLMs
   1. Self hosted
   2. full control over data and logic
   3. can run offline or on edge devices
   4. need heavy GPU/CPU requirements
   5. need to handle updates, optimization, memory.
6. Agents- LLM that can take actions using tools or API.
7. RAG- LLM with a database or search engine to access up to date facts before generating response.
8.  Research shows that context stuffing can quickly degrade the performance of LLMs. Anything beyond a couple thousand tokens will experience decreased recall, particularly for information in the middle of a prompt.
9.  conversational memory is simple: rather than sending just the most recent interaction to our LLM, we send a history of interactions + the most recent interaction to our LLM — typically in a chat log style format.

## RAG
| Feature             | Traditional RAG                      | Agentic RAG                              |
| ------------------- | ------------------------------------ | ---------------------------------------- |
| Query understanding | One-shot, static                     | Multi-step reasoning                     |
| Retrieval           | From one knowledge base              | From multiple data sources               |
| Tool usage          | None                                 | Uses APIs, calculators, browsers         |
| Memory              | No memory                            | Has short-term and long-term memory      |
| Adaptability        | Needs prompt tuning                  | Self-adapts, plans, and improves         |
| Example analogy     | Good student answering with textbook | Research assistant with tools and a plan |


