import streamlit as st
import streamlit_authenticator as stauth
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client,Client
import fitz
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import ChatGoogleGenerativeAI
import numpy as np


logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs("logs/app", exist_ok=True)
log_file = f"logs/app/{timestamp}.log"

handler=logging.FileHandler(log_file) #trying to save log file with date  and time, idk if that will work. Let's see
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

supabaseUrl = os.getenv("supabase_url")
supabaseKey =os.getenv("supabase_api_key")
supabase = create_client(supabaseUrl, supabaseKey)
GOOGLE_API_KEY= os.getenv("GEMINI_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=GOOGLE_API_KEY)
doc_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07",task_type="RETRIEVAL_DOCUMENT")
query_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07", task_type="RETRIEVAL_QUERY"
)
st.title("QnA chatbot")
if not st.session_state.get("logged_in", False):
    signup = st.button("Sign Up") 
    login = st.button("Log In")

    if signup: 
        logger.info("Form state set to signup")
        st.session_state["form_state"] = "signup"
    if login:
        logger.info("Form state set to login")
        st.session_state["form_state"] = "login"


def get_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip().replace("\n", " ")

def chunk_text(text):
    logger.info("Entered chunk_text function")
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
    except Exception as e:
        logger.error(f"Error generating chunks: {e}")
    logger.info("Exiting chunk_text function.")
    return splitter.split_text(text)


def get_embeddings(chunks):
    logger.info("Entered get_embeddings funtion")
    return doc_embeddings.embed_documents(chunks)

def delete_file_and_chunks(file_id):
    logger.info("Entered delete file function.")
    try:
        supabase.table("chunks").delete().eq("file_id", file_id).execute()
        supabase.table("uploaded_files").delete().eq("id", file_id).execute()
    except Exception as e:
        logger.error(f"Error deleting files: {e}")
    logger.info("Exiting delete file function")


def loggedin():
    st.sidebar.success(f"Welcome,{st.session_state.get('user_email','User')} to your Dashboard!")
    st.sidebar.header("Uploaded Files")
    prompt=st.text_input("Enter your Prompt!")
    st.subheader("Response:")  
    output=st.empty()
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
        
    user_email = st.session_state.get("user_email")
    if not user_email:
        logger.warning("Can not find the email")
    st.subheader("Welcome to the QnA Dashboard!")
    try:
        files = supabase.table("uploaded_files")\
            .select("*")\
            .eq("user_email", user_email)\
            .execute().data
    except Exception as e:
        logger.warning(f"File fetching failed {e}")
        st.warning("No files found.")
    try:
        for file in files:
            with st.sidebar.expander(file["file_name"]):
                st.write("Uploaded on:", file["upload_time"].split("T")[0])
                if st.button(f"🗑 Delete {file['file_name']}", key=file["id"]):
                    delete_file_and_chunks(file["id"])
                    st.success(f"{file['file_name']} deleted")
                    st.rerun()
    except:
        logger.error(f"some error: {e}")
        
        
    uploaded_files= st.file_uploader("Upload the files here.",accept_multiple_files=True, type=['pdf'])
    if uploaded_files:
        try: 
            for uploaded_file in uploaded_files:
                st.write(f"**Filename:** {uploaded_file.name}")
                file_bytes = uploaded_file.read()
                if file_bytes:
                    logger.info(f"file bytes recieved.")
                file_hash = get_file_hash(file_bytes)
                if file_hash:
                    logger.info(f"got file hash.")
                
                existing = supabase.table("uploaded_files")\
                    .select("*")\
                    .eq("user_email", user_email)\
                    .eq("file_hash", file_hash)\
                    .execute()
                
                if existing.data:
                    logger.info(f"Existing data in the uploaded_files table. {existing}")
                    st.warning(f"You already uploaded {uploaded_file.name}")
                    continue  
                
                response1 = supabase.table("uploaded_files").insert({
                    "user_email": user_email,
                    "file_name": uploaded_file.name,
                    "file_hash": file_hash
                }).execute()
                if response1:
                    logger.info(f"insertion done. {response1}")
                    logger.info(f"response data:{response1.data}")
                file_id = response1.data[0]["id"]
                text= extract_text_from_pdf(uploaded_file)
                if text:
                    logger.info("successfully extracted the text.")
                
                chunks= chunk_text(text)
                
                if chunks:
                    logger.info(f"chunks recieved {chunks}")
                
                embeddings = get_embeddings(chunks)
                
                if embeddings:
                    logger.info(f"embeddings recieved {embeddings}")
                    
                for chunk,embedding in zip(chunks,embeddings):
                    logger.info(f"inserting into the table chunks: file_id-{file_id},chunk:{chunk},embedding: {embedding}")
                    supabase.table("chunks").insert({
                        "file_id": file_id,
                        "chunk_text": chunk,
                        "embedding": embedding
                    }).execute()

                st.success(f"✅ {uploaded_file.name} uploaded and processed successfully!")
        except Exception as e:
            logger.info(f"some error in uploading and chunk generation {e}")

    submit=st.button("Submit")        
    try:
        if submit:
            prompt_embed=query_embeddings.embed_query(prompt)
            chunks_response= supabase.table("chunks").select("id,chunk_text,embedding,file_id").execute()
            if chunks_response:
                logger.info(f"Retrieved the chunks from the database: {chunks_response}")
            user_chunks=chunks_response.data
            
            files_response=supabase.table("uploaded_files").select("id,file_name").execute()
            if files_response:
                logger.info(f"Retrieved the filenames for the context: {files_response}")
                
            file_map={file["id"]: file["file_name"] for file in files_response.data}
            
            chunk_vectors = [np.array(chunk["embedding"]) for chunk in user_chunks]
            similarities = cosine_similarity([prompt_embed], chunk_vectors)[0]
            if similarities:
                logger.info(f"performed cosine similarity: {similarities}")
            k=3
            top_indices = np.argsort(similarities)[::-1][:k]
            top_chunks = [(user_chunks[i], similarities[i]) for i in top_indices]
            with st.expander("Matched Chunks:"):
                for chunk,score in top_chunks:
                    file_name=file_map.get(chunk["file_id"],"Unknown")
                    context="\n".join(chunk["chunk_text"])
                    st.markdown(f"**File:** {file_name}")
                    st.markdown(f"**Score:** {round(score, 4)}")
                    st.code(chunk["chunk_text"])
                    st.markdown("---")
            full_prompt=f"""You are a helpful RAG based assistant. Use the context below and answer the user question.
            Context: {context}
            Question: {prompt}
            """
            response=llm.invoke(full_prompt)
            if response:
                output.write(response.content)
            else:
                output.write("Error generating your response")
    except Exception as e: 
        logger.error(f"some error in the post submit part: {e}")

def sign_up():
    with st.form(key='signup',clear_on_submit=True):
        logger.info("Entered signup function")
        st.subheader(':green[Sign Up]')
        try:
            submitted=False
            email=st.text_input('Email', placeholder="Enter you Email")
            password1=st.text_input("Password",placeholder="Enter your password", type='password')
            password2=st.text_input("Confirm Password",placeholder="Enter your password", type='password')
            submitted=st.form_submit_button("Sign Up")
            if submitted:
                if password1!=password2:
                    st.write("Passwords don't match")
                else:
                    response=supabase.auth.sign_up(
                        {
                            "email": email,
                            "password":password1,
                        }
                    )
                    if response.user:
                        logger.info(f"Recieved response {response.user}")
                        st.success("Account created! Please check you email to verify account and log in once verified.")
                        st.session_state["form_state"]="login"
                        logger.info(f"set the session state as: {st.session_state['form_state']}")
        except Exception as e:
            st.error("Signup failed.")
            logger.error(f"Sign Up failed: {e}")
        logger.info("Exiting signup function")
        
def login():
    with st.form(key="login", clear_on_submit=True):
        logger.info("Entered login function")
        st.subheader(":green[Log in]")
        try:
            submitted=False
            email=st.text_input('Email', placeholder="Enter you Email")
            password=st.text_input("Password",placeholder="Enter your password", type='password')
            submitted=st.form_submit_button("Log In")
            if submitted:
                response= supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password,
                        }
                    )
                if response.session:
                    logger.info(f"Response: {response.session}")
                    st.success("Login Successful!")
                    st.session_state["logged_in"]= True
                    logger.info(f"Set session state as {st.session_state['logged_in']}")
                    st.session_state["user_email"]=email
                    logger.info(f"set session state user email as {st.session_state['user_email']}")
                
    
        except Exception as e:
            st.error("Login Failed")
            logger.error(f"Login Failed: {e}")
        logger.info("Exiting login function")
            
if "form_state" not in st.session_state:
    st.session_state["form_state"] = ""      
        
if st.session_state["form_state"] == "login":
    login()
if st.session_state.get("logged_in", False):
    loggedin()
elif st.session_state["form_state"] == "signup":
    sign_up()