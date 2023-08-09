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

load_dotenv()


# %%
class DocBot:
    ############## Embedder and DB
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_directory = (
        "c:\\Users\\Payoff\\Desktop\\chatbot\\flask\\db\\vectorStore\\chromadb"
    )
    vector_store = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    vector_store_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    ############## LLM model
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(model_name=model_name, temperature=0)

    ############## Prompt
    template = """
        Use chat history : {chat_history} to determine the condition you are to research if not blank
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

    def __init__(self, history_number=5):
        # self.chat_history = chat_history
        self.history_number = history_number

        self.memory = ConversationBufferWindowMemory(
            k=self.history_number, memory_key="chat_history", output_key="answer"
        )  # return_messages=True

        # conversational Retrieval Chain
        self.conversational_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store_retriever,
            memory=self.memory,
            chain_type="stuff",
            return_source_documents=True,
            return_generated_question=True,
            combine_docs_chain_kwargs={"prompt": self.prompt},
            get_chat_history=lambda h: h,
        )

    def get_response(self, question, chat_history=[]):
        with get_openai_callback() as cb:
            result = self.conversational_chain(
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

        chat_history.append({"question": question, "answer": result["answer"]})

        response = {
            "result": result,
            "prompt": {
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens,
                "total_cost": cb.total_cost,
            },
        }

        return response, chat_history


# %%

# agent = DocBot()

# question = "cosa e invoice date della WORLD FUEL SERVICE SINGAPORE ?"
# res, chat_history = agent.get_response(question)
# print("res:   ", res)
# print("chat_history:   ", chat_history)
# print("answer:", res["result"]["answer"])


# %%
