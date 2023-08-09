# %%
import os
from dotenv import load_dotenv
import openai
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback

# %%
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "/flask/db/vectorStore/chromadb"
vectorStore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
# %%
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

model_name = "gpt-3.5-turbo"
llm = ChatOpenAI(model_name=model_name, temperature=0)
# print(llm.predict("Hello Bot!"))
# %%
# ## Make a retriever
vectorStoreRetriever = vectorStore.as_retriever(search_kwargs={"k": 3})
# %% The prompt
template = """Use chat history : {chat_history} to determine the condition you are to research if not blank

Use the following pieces of context to answer the question at the end.
{context}
If you still cant find the answer, just say that you don't know, don't try to make up an answer.
You can also look into chat history.
{chat_history}
Question: {question}
Answer:
"""
prompt = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template=template,
)
# %% conversational Retrieval Chain
memory = ConversationBufferWindowMemory(
    k=5, memory_key="chat_history", output_key="answer"
)  # return_messages=True

conversational_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorStoreRetriever,
    memory=memory,
    chain_type="stuff",
    return_source_documents=True,
    return_generated_question=True,
    combine_docs_chain_kwargs={"prompt": prompt},
    get_chat_history=lambda h: h,
)
# %%

##chat_history = []
# question = "Exchange Rate of WORLD FUEL SERVICE SINGAPORE5"
# result = conversational_chain({"question": question, "chat_history": chat_history})
# # result = conversational_chain({"question": question})
# print(result)
# print(result["answer"])

# %%
chat_history = []


def getResponse(question):
    with get_openai_callback() as cb:
        result = conversational_chain(
            {"question": question, "chat_history": chat_history}
        )

        print(result["answer"])
        print("\n\nSources:")
        for source in result["source_documents"]:
            print(source.metadata["source"])

        print("--------------------------------")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")
        chat_history.append((question, result["answer"]))


# %%
# question = "invoice date?"
# getResponse(question)
# %%
