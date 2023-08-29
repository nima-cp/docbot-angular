# %%
import os
import openai
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback
from langchain.document_loaders import UnstructuredMarkdownLoader


from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


openai.api_key = os.getenv("OPENAI_API_KEY")

# %%

markdown_path = "./report.md"
loader = UnstructuredMarkdownLoader(markdown_path)
data = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=10)
all_splits = text_splitter.split_documents(data)
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())


reports = [
    "La segnalazione con identificativo: 0242ac120002 è stata aggiornata dall'utente segnalatore in data 21/11/2022.",
    "La segnalazione con identificativo: 37c3b48eb060 è stata aggiornata dall'utente segnalatore in data 22/11/2022.",
    "La segnalazione con identificativo: 690b5a è stata aggiornata dall'utente segnalatore in data 23/11/2022.",
    "La segnalazione con identificativo: 2581d è stata aggiornata dall'utente segnalatore in data 24/11/2022.",
    "E' stato creata una nuova segnalazione con identificativo: 74daa5bb in data 25/11/2022 di Abuso per il reparto Amministrazione che deve essere gestita da Roberto. La pratica è disponibile all'indirizzo: https://segnalazione/id1. La segnalazione non è stata presa in carico",
    "E' stato creata una nuova segnalazione con identificativo: a1b02c2 in data 26/11/2022 di Frode per il reparto Magazzinoche deve essere gestita da Francesco. La pratica è disponibile all'indirizzo: https://segnalazione/id6. La segnalazione non è stata presa in carico",
    "La segnalazione con identificativo: 74daa5bb è stata aggiornata dall'utente Alex segnalatore in data 28/11/2022.",
    "La segnalazione con identificativo: 690b5a è stata presa in carico dall'utente Alberto",
    "E' stato creata una nuova segnalazione con identificativo: 237868 in data 28/11/2022 di Razzismo per il reparto Magazzino che deve essere gestita da Alex. La pratica è disponibile all'indirizzo: https://segnalazione/id8. La segnalazione non è stata presa in carico. la data di scadenza è il 30/11/2022",
    "La segnalazione con identificativo: 74daa5bb è stata presa in carico dall'utente Andrea",
    "La segnalazione con identificativo: 0242ac120002 è stata presa in carico dall'utente Francesca e lo stato e in lavorazione",
    "La segnalazione con identificativo: a1b02c2 è stata presa in carico dall'utente Nima",
    "Tutto le segnalazioni sono aperti",
    "La segnalazione con identificativo: 37c3b48eb060 è stata chiusa da John il 05/12/2022",
]

# %%


class DocBot:
    markdown_path = "./report.md"
    loader = UnstructuredMarkdownLoader(markdown_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)
    vector_store = Chroma.from_documents(
        documents=all_splits, embedding=OpenAIEmbeddings()
    )

    vector_store_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    query = "quanti ci sono le segnalazioni"
    docs = vector_store_retriever.get_relevant_documents(query)
    print(docs)
    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(model_name=model_name, temperature=0)

    ############## Prompt
    # instruction = """Cronologia della chat:\n\n{chat_history} \n\nUtente: {user}\n\n assistente:"""
    instruction = """Utilizza i seguenti elementi di contesto per rispondere alla domanda alla fine.
        {context}
        Puoi anche esaminare la cronologia della chat.
        {chat_history}
        Domanda: {question}"""
    system_prompt = """Sei un utile assistente italiano. Il tuo compito è aiutare gli utenti di un sito di Whistleblowing a gestire le attività legate alle segnalazioni.
    Identificazione e classificazione dei report in base al loro stato (es. "nuovo", "in corso", "completato", "archiviato"), chi ha creato il report, chi ne è responsabile e quando è la data di scadenza.

    Se non sei sicuro, dì non lo so.
    Rispondi con risposte brevi e precise, senza alcuna elaborazione in italiano.
    """

    def get_prompt(instruction, new_system_prompt):
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
        prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
        return prompt_template

    template = get_prompt(instruction, system_prompt)

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template,
    )

    def __init__(self, history_number=10):
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
agent = DocBot()
# %%


# question = f"{reports} \n\nquanti ci sono le segnalazioni?"
question = "quanti le segnalazioni sono chiusi?"
question = "quale la e?"
question = 'ordinare i report in base alla data. metti prima il più recente e per ultimo il più vecchio'
question = 'sono Nima, quale la segnalazione e presa in carica per me?'
question = 'quale lo stato dela segnalazione e in lavorazione'
question = 'quale la segnalazione e abuso? dammi l"indirizzo e il reparto e id'

response = agent.get_response(question)
print("response:   ", response)


# %%


# %%
