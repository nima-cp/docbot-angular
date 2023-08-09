# %%
# from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import Chroma

# %% Deleting the DB
# # To cleanup, you can delete the collection
# vectorStore.delete_collection()
# vectorStore.persist()
# %%
filePath = "../docs"
# Load and process the text files
loader = DirectoryLoader(filePath, glob="./*.pdf", loader_cls=PyMuPDFLoader)
pages = loader.load_and_split()

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
persist_directory = "../db/vectorStore/chromadb"

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

