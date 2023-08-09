# %% Deleting the DB
# To cleanup, you can delete the collection
from langchain.vectorstores import Chroma

persist_directory = "../db/vectorStore/chromadb"
vectorStore = Chroma(persist_directory=persist_directory)
vectorStore.delete_collection()
vectorStore.persist()

print("Database deleted successfully")
# %%
