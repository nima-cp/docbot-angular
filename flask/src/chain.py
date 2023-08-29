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
    """
    A conversational AI bot that uses a combination of language models, embeddings, and conversation memory.

    Attributes:
        embeddings
        vector_store (Chroma): Vector store for document retrieval.
        vector_store_retriever (Chroma.Retriever): Retriever for document retrieval.
        llm (ChatOpenAI): Chat model for language generation.
        template (str): Prompt template for generating context-aware responses.
        prompt (PromptTemplate): Prompt generator based on the template.
        memory (ConversationBufferWindowMemory): Conversation memory for retaining chat history.
        conversational_chain (ConversationalRetrievalChain): Conversational retrieval chain for generating human-like responses.

    Methods:
        __init__(self, history_number=5): Constructor to initialize the DocBot instance.
        get_response(self, question: str, chat_history=[]): Get a response from the bot given a question and optional chat history.
    """

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
        You are a helpful multilingual AI assistant. Answer in the same language as the question at the end.
        Use chat history : {chat_history} to determine the condition you are to research if not blank
        Use the following pieces of context to answer the question at the end.
        {context}
        If you still can't find the answer, just say that you don't know, don't try to make up an answer.
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
            # return_generated_question=True,
            combine_docs_chain_kwargs={"prompt": self.prompt},
            get_chat_history=lambda h: h,
        )

    def get_response(self, question: str, chat_history=[]):
        """
        Generate a response to a given question.

        Args:
            question (str): The question posed to the bot.
            chat_history (list, optional): List of chat history dictionaries. Defaults to an empty list.

        Returns:
            dict: A dictionary containing the generated response, chat history, and prompt details.
        """
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

        # chat_history.append({"question": question, "answer": result["answer"]})

        response = {
            "result": {
                "question": question,
                "answer": result["answer"],
                "chat_history": chat_history,
            },
            "prompt": {
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens,
                "total_cost": cb.total_cost,
            },
        }

        return response


# %%

# agent = DocBot()

# question = "cosa e invoice date della WORLD FUEL SERVICE SINGAPORE ?"
# response = agent.get_response(question)
# print("response:   ", response)
# print("answer:", response["result"]["answer"])


# %%


# %%
