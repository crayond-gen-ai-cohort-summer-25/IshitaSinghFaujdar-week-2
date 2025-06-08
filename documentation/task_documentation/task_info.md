# Task Explanation
1. This project in entirety is in try and catch blocks with logging to debug better the issues.
2. I started off with initializing supabase variables. I chose supabase because I had already worked with it before and was very familiar with it.
3. I started developing the login and sign up functions first. This entire coding is botom to top.
4. I wanted the login and sign up functions so that I can keep everyone's data seperate instead of maintaining a session state everytime. That way it's easier to segregate and manage embeddings as well.
5. I used streamlit and that was also one of the reasons everything was in a try and catch block because streamlit throws big error when a function fails on the user side.
6. I used form state and rerun() to go from login to sign up to logged in. Only flaw in this I feel is that there is no 'go back' option and you auto logout when you reload.
7. Once we enter loggedin function, I start by showing any previously uploaded files by the user. Then there are options to upload more files and enter prompt.
8. When we upload a file once, it undergoes extraction using PDF PLUMBER and then get's chunked.There is a fixed character size but also the last 100 characters are also taken and added to context in case we may miss out anything(like cutting off mid sentance). This was better than the fixed size and the semantic chunking. I felt in the first one i might lose context and in the second one the context might get too big.
9. Then embeddings are generated and you can then press on cross on your uploaded files, you will see them in the uploaded files section.
10. You can then go ahead and enter a prompt. It will undergo chunking and embedding generation as well.
11. Then the embeddings are retrieved with cosine similarity score. I haven't used a threshold but mentioned that I want the top 5 returned embeddings to be used as context.
12. Once you delete a file from your uploaded section the chunks also get deleted.
13. In supabase, thre are 2 tables, chunks and uploaded_files which are used to map data which I have mentioned in my pre-planning phase as well.
14. Regarding embedding model, the model I used earlier was the new experimental model but ran out of limit so switched to the mdel I wa currently using.
15. Coming back, the context and user query is appended and sent as a prompt to gemini and the response is printed and the chunks with file names which were used for context are also displayed.