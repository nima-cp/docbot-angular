"""
Document Embedding and Indexing Process

This file demonstrates the process of document embedding and indexing using various techniques.
It includes configurations, steps, and examples of embedding documents, creating a vector store,
and performing similarity search.

Dependencies:
- langchain.embeddings
- langchain.text_splitter
- langchain.document_loaders
- langchain.vectorstores

Usage:
- Configure the file path where the documents are located (filePath).
- Load and process text files using DirectoryLoader and PyMuPDFLoader.
- Split the documents into smaller chunks using RecursiveCharacterTextSplitter.
- Choose an embedding technique (OpenAIEmbeddings, HuggingFaceEmbeddings, SentenceTransformerEmbeddings).
- Create a Chroma vector store for indexing and storing document embeddings.
- Persist the vector store to disk.
"""
# %%
# from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import UnstructuredXMLLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()
# %%
persist_directory = (
    "c:\\Users\\Payoff\\Desktop\\chatbot\\flask\\db\\vectorStore\\chromadb"
)
collection_name = os.getenv("COLLECTION_NAME")


# %%

filePath = "c:\\Users\\Payoff\\Desktop\\chatbot\\docs"
# Load and process the text files
loader = DirectoryLoader(
    filePath,
    glob="./*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True,
)

# loader = DirectoryLoader(
#     filePath,
#     glob="./*.xml",
#     loader_cls=UnstructuredXMLLoader,
#     show_progress=True,
# )
# documents = loader.load()


# filePath = "c:\\Users\\Payoff\\Desktop\\chatbot\\docs\\2023-05-INZZM0001-VOCI .csv"
# loader = CSVLoader(
#     filePath,
#     csv_args={
#         "delimiter": ";",
#         "quotechar": '"',
#     },
#     # source_column="Name"
# )

# documents = loader.load()

# loader = DirectoryLoader(
#     filePath,
#     glob="./*.xml",
#     loader_cls=UnstructuredXMLLoader,
#     show_progress=True,
# )
# pages = loader.load_and_split()

documents = loader.load()

# %%


def split_docs(documents, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splitted_docs = text_splitter.split_documents(documents)
    return splitted_docs


splitted_docs = split_docs(documents)


# ### Embeddings
# Choose one of the following embeddings options

################################
## here we are using OpenAI embeddings
# import os
# import openai
# openai.api_key = os.getenv("OPENAI_API_KEY")
# embeddings = OpenAIEmbeddings()

################################
# from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
# model_name = "sentence-transformers/all-mpnet-base-v2"
# hf = HuggingFaceEmbeddings(model_name=model_name)

################################
# from langchain.embeddings import HuggingFaceInstructEmbeddings

# embeddings = HuggingFaceInstructEmbeddings(
#     model_name="hkunlp/instructor-xl",
#     model_kwargs={"device": "cuda"},  # or cpu for CPU
# )


from langchain.embeddings import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


### create the DB
# Embed and store the docs
# Supplying a persist_directory will store the embeddings on disk
vectorStore = Chroma.from_documents(
    documents=splitted_docs, embedding=embeddings, persist_directory=persist_directory
)


# persiste the db to disk
vectorStore.persist()


# query = "logistic regression"
# matching_docs = vectorStore.similarity_search_with_score(query, k=4)
# print(matching_docs)


# query = "gross amount of bp oil"
# docs = vectorStoreRetriever.get_relevant_documents(query)
# docs


print("ingest is done")
# %%

# vector_store_retriever = vectorStore.as_retriever(search_kwargs={"k": 5})
# # query = "data di nascita in PRVDNB60A29L840Y___1_2"
# # matching_docs = vectorStore.similarity_search_with_score(query, k=5)
# # matching_docs
# # # %%
# query = "Minimo Contr in PRVDNB60A29L840Y___1_2"
# docs = vector_store_retriever.get_relevant_documents(query)
# docs
# %%
