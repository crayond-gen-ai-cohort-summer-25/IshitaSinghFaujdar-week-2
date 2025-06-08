# Task Planning

## Deliverables
### Phase 1
1. Interface to upload PDFs
   1. Streamlit can be used
   2. upload files button should be there to upload multiple files
2. Extract text from PDFs
   1. Libraries like pymupdf or pdfplumber or pdfminer can be used.
   2. extract raw text
   3. clean the text by removed newlines, whitespaces etc.
3. Chunking
   1. For this I am not sure, we'll see which performs well. Langchain's text splitter can be used.
   2. Creating chunks of 300-500 tokens with semantic sense.
4. Generate Embeddings
   1. Gemini embedding model can be used.
   2. Need to convert each chunk into dense vector
5. Store embeddings in vector db
   1. we'll use supabase for this
### Phase 2
1. Need a user input box to ask questions
2. should convert question to embeddings.
3. Perform a similarlity search in documents.
> For this, I need a user login as well so no one can just query through the database just like that.
5. Once the chunks are retrieved, they have to be used as context or prompt and sent to LLM to answer the question
### Phase 3
1. Testing with multiple queries
2. When showing the final answer, also need to show the documents and chunks used.
3. Validation to check for hallucination


## UI planning
1. To avoid the users to access databases that are not uploaded by them I need to add a session state. I am thinking of adding a login layer but also I am thinking if no login process then I will have to assign a session id and store with that and delete it once it's done. This looks more complicated so I am thinking of going ahead with the login/ sign up layer.
2. 
## Function planning
This was probably the most time consuming part.

## Database
For database, I am not storing the user files, just the chunks in the table chunks and the file metadata in the the uploaded_files table.
Idea is that in case multiple files are uploaded it will return the file name as well.

uploaded_files
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_email TEXT,
file_name TEXT,
file_hash TEXT,
upload_time
chunks
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
file_id UUID REFERENCES uploaded_files(id),
chunk_text TEXT,
embedding vector(768) 
