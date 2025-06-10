import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client,Client
from langchain_google_genai import ChatGoogleGenerativeAI
#Logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"main_{timestamp}.log")


handler=logging.FileHandler(log_file) #trying to save log file with date  and time, idk if that will work. Let's see
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
    
#API and other setup
load_dotenv()

supabaseUrl = os.getenv("supabase_url")
supabaseKey =os.getenv("supabase_api_key")
supabase = create_client(supabaseUrl, supabaseKey)
GEMINI_KEY=os.getenv("GEMINI_KEY")
with open("schema_context.txt", "r") as f:
    schema_context = f.read()
    print(schema_context)
def load_llm():
    GOOGLE_API_KEY = os.getenv("GEMINI_KEY")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=GOOGLE_API_KEY)

llm = load_llm() 


def generate_sql(user_query):
    try:
        prompt=f""" 
        You are a helpful AI assistant that converts natural language questions into SQL queries.
        The database is about budgeting and finance.
        Always use single quotes (' ') for string values (e.g., WHERE name = 'John'), and double quotes for identifiers only when needed.
        Use PostgreSQL syntax. For example, to filter for "this month", use:
  t.transaction_date >= date_trunc('month', CURRENT_DATE)
  AND t.transaction_date < date_trunc('month', CURRENT_DATE + interval '1 month')

        General Instructions:
- If user-specific filtering is needed, always filter using: u.user_id = {{user_id}} (with curly braces).
- Do NOT hardcode any user ID. Leave a placeholder like {{user_id}} for replacement.
- To get current month's expenses, use transaction_date and filter by the current month.
- To summarize expenses per category or date range, group by category_id or transaction_date.
    Below is the schema context and a user's question. Generate a correct SQL query only.
        Question:
    {user_query}
    This is what I ran in my database. Table names are in not caps.
    CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);

CREATE TABLE Accounts (
    account_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    account_name TEXT,
    balance NUMERIC
);

CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE Transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES Accounts(account_id),
    category_id INTEGER REFERENCES Categories(category_id),
    amount NUMERIC,
    transaction_date DATE,
    description TEXT
);

CREATE TABLE Budgets (
    budget_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    category_id INTEGER REFERENCES Categories(category_id),
    monthly_limit NUMERIC
);
Relationships:
- One user can have many accounts.
- Each account can have many transactions.
- Each transaction is associated with a category.
- Budgets are per user per month/year.





    Only return SQL query. No explanations.
        """
        logger.info("Generating SQL query from LLM. (generate_sql function)")
        response=llm.invoke(prompt)
        sql_query=response.content.strip("```sql").strip("```").strip().rstrip(';')
        logger.debug(f"Generated query: {sql_query}")
    except Exception as e:
        logger.error(f"Error generating sql: {e}")
    return sql_query
def run_sql(query):    
    logger.info("Running SQL query on Supabase. (run_sql function)")
    result = supabase.rpc("run_sql", {"query": query}).execute()
    if hasattr(result, 'data') and result.data:
        return result.data
    else:
        logger.warning("No data returned from Supabase.")
        return []
def format_result(query,result):
    try:
        prompt = f"""
    You are a finance assistant. Format the SQL result below into a clear one-line answer.

    User Question: {query}
    SQL Result: {result}

    Answer:
    """
        logger.info("Formatting output using LLM. (format_result function)")
        response =llm.invoke(prompt)
    except Exception as e:
        logger.error(f"Error formatting result:{e}")
    return response.content.strip()

def get_user_input():
    while True:
        user_id=input("Please enter your user id to continue. \n")
        query=input("What's your Question? Enter exit if you want to quit.\n")
        if query.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            break
        
        logger.debug(f"USER PROMPT:{query}")
        sql_query=generate_sql(query)
        if "{user_id}" in sql_query:
            sql_query = sql_query.replace("{user_id}", str(user_id))
            if not sql_query:
                logger.error("SQL query generation failed. ")
                print("Error responding to your response")
                exit
        try:
            result=run_sql(sql_query)
            logger.info(f"Ran the sql query. Response: {result}")
        except Exception as e:
            logger.error(f"Error with running query:{e}")
            continue
        response=format_result(query,result)
        logger.debug(f"AI RESPONSE: {response}")
        print(response)


get_user_input()