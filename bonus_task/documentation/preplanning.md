# Finance Tracker
##  Objective:
I am trying to build an AI system that takes a Natural Language question, understands my db, converts the question into an acurate SQL query and returns a human readable answer.
Example question: 
How much money did I spend on groceries this month?
Fetches, converts, runs SQL, formats again, displays results.
Result: You spent 3000 on groceries in May 2025.

## Basic Architecture
### Database Layer: PostgreSQL(supabase)
    tables:
   1. Users
   2. Accounts
   3. Categories
   4. Transactions
   5. Budgets


COMMANDS RUN IN SUPABASE:
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
For fake data I searched and it said to use `faker`
### Understanding Layer
Basic understanding file for LLM's context
A file with :
1. Table description
2. Column descriptions
3. Relationships
4. Sample queries

### LLM Layer
Here we take input from user, pass it to LLM with user prompt and the schema.
The LLM should reply with a query.
Which should be run in supabase. Once results fetched, it should be sent back to the LLM for better reply.


Then we will proceed with testing.