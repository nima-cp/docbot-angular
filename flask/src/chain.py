# %%
import os
import openai
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.vectorstores import Chroma

# from langchain.chains.question_answering import load_qa_chain ## costly
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import SentenceTransformerEmbeddings

# %%

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "../db/vectorStore/chromadb"
vectorStore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)


# %%
question = "regression"
matching_docs = vectorStore.similarity_search(question, k=3)
print(matching_docs)

# %%
# ## Make a chain
#
# llm parameter is set to OpenAI(), which is the base class for all OpenAI models. This means that the RetrievalQA model will use a generic OpenAI model, without any specific hyperparameters or focus.
#

# %%
# openai.api_key = os.getenv("OPENAI_API_KEY")

model_name = "gpt-3.5-turbo"
llm = ChatOpenAI(model_name=model_name, temperature=0)
# print(llm.predict("Hello Bot!"))
# %%
# ## Make a retriever
vectorStoreRetriever = vectorStore.as_retriever(search_kwargs={"k": 3})
# %% The prompt
from langchain.prompts import PromptTemplate

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
# %%
# # Run chain
# # question = "what is random forest"

# qa_chain = RetrievalQA.from_chain_type(
#     llm,
#     retriever=vectorStoreRetriever,
#     chain_type="stuff",
#     return_source_documents=True,
# chain_type_kwargs={"prompt": prompt},
# )

# result = qa_chain({"query": question})
# print(result)
# print(result["result"])


# %% conversational Retrieval Chain
from langchain.memory import ConversationBufferWindowMemory

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

chat_history = []
question = "Exchange Rate of WORLD FUEL SERVICE SINGAPORE5"
result = conversational_chain({"question": question, "chat_history": chat_history})
# result = conversational_chain({"question": question})
print(result)
print(result["answer"])

# %%
chat_history.append((question, result["answer"]))
# question = "can you translate the last message in italian?"
question = "divide that number by 2?"

result = conversational_chain({"question": question, "chat_history": chat_history})
print(result)
print(result["answer"])


# %%
## Cite sources
def process_llm_response(result):
    print(result["answer"])
    print("\n\nSources:")
    for source in result["source_documents"]:
        print(source.metadata["source"])


# %%
# example
question = "what is the iban of WORLD FUEL SERVICE SINGAPORE5"
result = conversational_chain({"question": question, "chat_history": chat_history})
process_llm_response(result)

# %%
# break it down
# question = "qual è amount e quantity di l'airport fee e quale pagina e quale documento è la risposta?"
question = "invoice total and due date of bp oil hellenic"

with get_openai_callback() as cb:
    result = conversational_chain({"question": question, "chat_history": chat_history})
    process_llm_response(result)

    print("--------------------------------")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost}")

# %%
