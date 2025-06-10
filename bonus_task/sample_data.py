import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client,Client
from faker import Faker
import random
#Logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"sample_data_{timestamp}.log")


handler=logging.FileHandler(log_file) #trying to save log file with date  and time, idk if that will work. Let's see
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info(" Starting procedure")    
#API and other setup
load_dotenv()

supabaseUrl = os.getenv("supabase_url")
supabaseKey =os.getenv("supabase_api_key")
supabase = create_client(supabaseUrl, supabaseKey)

fake=Faker()

def reset_tables():
    logger.info("Entered Reset table function.")
    try:
        supabase.table("budgets").delete().neq("budget_id", 0).execute()
        supabase.table("transactions").delete().neq("transaction_id", 0).execute()
        supabase.table("categories").delete().neq("category_id", 0).execute()
        supabase.table("accounts").delete().neq("account_id", 0).execute()
        supabase.table("users").delete().neq("user_id", 0).execute()

        logger.info(f"Executed. All tables reset successfuly")
    except Exception as e:
        logger.error(f"Reset table error: {e}")
        
def insert_users(n=50):
    logger.info("Entered the insert users function")
    user_ids=[]
    try:
        for _ in range(n):
            name=fake.name()
            email=fake.unique.email()
            res = supabase.table("users").insert({"name": name, "email": email}).execute()
            logger.info(f"Inserted into users, recieved response: {res}")
            if res.data:
                uid = res.data[0]["user_id"]
                logger.info(f"uid:{uid}")
                user_ids.append(uid)
            else:
                logger.error("No user_id returned")
        logger.info(f"User IDS: {user_ids}")    
    except Exception as e:
        logger.error(f"Error in inserting in users table: {e}")
    return user_ids


def insert_accounts(user_ids):
    logger.info("Inserting accounts function")
    acc_ids = []
    try:
        for uid in user_ids:
            for _ in range(random.randint(1, 2)):
                acc_name = fake.word().capitalize() + " Account"
                balance = round(random.uniform(1000, 10000), 2)
                res = supabase.table("accounts").insert({
                    "user_id": uid,
                    "account_name": acc_name,
                    "balance": balance
                }).execute()
                logger.info(f"Inserted into accounts, recieved response: {res}")
                acc_ids.append(res.data[0]['account_id'])
        logger.info(f"account ids: {acc_ids}")
    except Exception as e:
        logger.error(f"Error in inserting accounts:{e}")
    return acc_ids

def insert_categories():
    logger.info("Inserting categories function")
    names = ['Food', 'Rent', 'Groceries', 'Transport', 'Entertainment', 'Utilities']
    cat_ids = []
    try:
        for name in names:
            res = supabase.table("categories").insert({"name": name}).execute()
            cat_ids.append(res.data[0]['category_id'])
        logger.info("Exiting insert categories")
    except Exception as e:
        logger.error(f"Error in insert categories: {e}")
    return cat_ids

def insert_transactions(account_ids, category_ids, n=200):
    logger.info("Inserting transactions.")
    try:
        for _ in range(n):
            acc = random.choice(account_ids)
            cat = random.choice(category_ids)
            amount = round(random.uniform(100, 50000), 2)
            date = fake.date_between(start_date="-90d", end_date="today").isoformat()
            desc = fake.sentence(nb_words=3)
            res=supabase.table("transactions").insert({
                "account_id": acc,
                "category_id": cat,
                "amount": amount,
                "transaction_date": date,
                "description": desc
            }).execute()
            logger.info(f"Transacction insertion status: {res}")
    except Exception as e:
        logger.error(f"Error in inserting transactions: {e}")

def insert_budgets(user_ids, category_ids):
    logger.info("Inserting budgets.")
    try:
        for uid in user_ids:
            for cid in category_ids:
                limit = round(random.uniform(1000, 8000), 2)
                res=supabase.table("budgets").insert({
                    "user_id": uid,
                    "category_id": cid,
                    "monthly_limit": limit
                }).execute()
                logger.info(f" budget insertion status: {res}")
    except Exception as e:
        logger.error(f"Error in inserting budgets: {e}")
            
logger.info("Starting MAIN function of sample_data.py")
reset_tables()
users = insert_users()
accounts = insert_accounts(users)
categories = insert_categories()
insert_transactions(accounts, categories)
insert_budgets(users, categories)
logger.info("process finished.")