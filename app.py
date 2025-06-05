import streamlit as st
import streamlit_authenticator as stauth
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client,Client

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
st.title("QnA chatbot")
signup=st.button("Sign Up") 
login=st.button("Log In")

if signup: 
    logger.info("Form state set to signup")
    st.session_state["form_state"] = "signup"
if login:
    logger.info("Form state set to login")
    st.session_state["form_state"] = "login"
    
    
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
elif st.session_state["form_state"] == "signup":
    sign_up()