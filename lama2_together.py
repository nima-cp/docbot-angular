# %%
# first activate the env:
# conda activate together
import together
from typing import Any, Dict, List

from pydantic import Extra, Field, root_validator

from langchain.llms.base import LLM
from langchain.utils import get_from_dict_or_env
import textwrap
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain, PromptTemplate

# import os
# from dotenv import load_dotenv

# load_dotenv()
# together_api_key: str =os.getenv["TOGETHER_API_KEY"]
# %%
together_api_key: str = (
    "98f05ad2c520b7de4c76cd49263c706e30c7857f386529c9bd1f11dd334c0f22"
)
# set your API key
together.api_key = together_api_key


# %%
class TogetherLLM(LLM):
    """Together large language models."""

    model: str = "togethercomputer/llama-2-7b-chat"
    """model endpoint to use"""

    together_api_key: str = together_api_key
    """Together API key"""

    temperature: float = 0.1
    """What sampling temperature to use."""

    max_tokens: int = 512
    """The maximum number of tokens to generate in the completion."""

    class Config:
        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the API key is set."""
        api_key = get_from_dict_or_env(values, "together_api_key", "TOGETHER_API_KEY")
        values["together_api_key"] = api_key
        print(values)
        return values

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "together"

    def _call(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Call to Together endpoint."""
        together.api_key = self.together_api_key
        output = together.Complete.create(
            prompt,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        text = output["output"]["choices"][0]["text"]
        print(text)
        return text


# %%
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
# DEFAULT_SYSTEM_PROMPT = """\
# You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

# If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""


def get_prompt(instruction, new_system_prompt):
    SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    return prompt_template


def cut_off_text(text, prompt):
    cutoff_phrase = prompt
    index = text.find(cutoff_phrase)
    if index != -1:
        return text[:index]
    else:
        return text


def remove_substring(string, substring):
    return string.replace(substring, "")


def parse_text(text):
    wrapped_text = textwrap.fill(text, width=100)
    print(wrapped_text + "\n\n")
    # return assistant_text


# llm = HuggingFacePipeline(pipeline = pipe, model_kwargs = {'temperature':0})

llm = TogetherLLM(model="togethercomputer/llama-2-70b-chat", temperature=0.1)

# %%
import uuid

reports: List[str] = [
    "La segnalazione con identificativo: 0242ac120002 è stata aggiornata dall'utente segnalatore in data 21/11/2022.",
    "La segnalazione con identificativo: 37c3b48eb060 è stata aggiornata dall'utente segnalatore in data 22/11/2022.",
    "La segnalazione con identificativo: 690b5a è stata aggiornata dall'utente segnalatore in data 23/11/2022.",
    "La segnalazione con identificativo: 2581d è stata aggiornata dall'utente segnalatore in data 24/11/2022.",
    "E' stato creata una nuova segnalazione con identificativo: 74daa5bb in data 25/11/2022 di Abuso per il reparto Amministrazione che deve essere gestita da Roberto. La pratica è disponibile all'indirizzo: https://segnalazione/id1. La segnalazione non è stata presa in carico",
    "E' stato creata una nuova segnalazione con identificativo: a1b02c2 in data 26/11/2022 di Frodeper il reparto Magazzinoche deve essere gestita da Francesco. La pratica è disponibile all'indirizzo: https://segnalazione/id6. La segnalazione non è stata presa in carico",
    "La segnalazione con identificativo: 74daa5bb è stata aggiornata dall'utente Alex segnalatore in data 28/11/2022.",
    "La segnalazione con identificativo: 690b5a è stata presa in carico dall'utente Alberto",
    "E' stato creata una nuova segnalazione con identificativo: 237868 in data 28/11/2022 di Razzismo per il reparto Magazzino che deve essere gestita da Alex. La pratica è disponibile all'indirizzo: https://segnalazione/id8. La segnalazione non è stata presa in carico. la data di scadenza è il 30/11/2022",
    "La segnalazione con identificativo: 74daa5bb è stata presa in carico dall'utente Andrea",
    "La segnalazione con identificativo: 0242ac120002 è stata presa in carico dall'utente Francesca e lo stato e in lavorazione",
    "La segnalazione con identificativo: a1b02c2 è stata presa in carico dall'utente Nima",
    "Tutto le segnalazioni sono aperti",
    "La segnalazione con identificativo: 37c3b48eb060 è stata chiusa da John il 05/12/2022",
]

# instruction = """report: \n\n{reports}\n\nCronologia della chat:\n\n{chat_history} \n\nUtente: {user}\n\n assistente:"""
instruction = (
    """Cronologia della chat:\n\n{chat_history} \n\nUtente: {user}\n\n assistente:"""
)
system_prompt = """Sei un utile assistente italiano. Il tuo compito è aiutare gli utenti di un sito di Whistleblowing a gestire le attività legate alle segnalazioni.
Identificazione e classificazione dei report in base al loro stato (es. "nuovo", "in corso", "completato", "archiviato"), chi ha creato il report, chi ne è responsabile e quando è la data di scadenza.

Se non sei sicuro, dì "Non lo so".
Rispondi con risposte brevi e precise, senza alcuna elaborazione in italiano.
"""


template = get_prompt(instruction, system_prompt)
print(template)

prompt = PromptTemplate(
    input_variables=["chat_history", "user"],
    template=template,
)
memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)


# %%
# llm_chain.predict(user=f"{reports} \n\ndammi tutto di la segnalazione 5")


# %%
llm_chain.predict(user=f"{reports} \n\nquanti ci sono i report")

# %%
llm_chain.predict(user="dammi tutti i rapporti di Amministrazione")

# %%
llm_chain.predict(user=f"{reports} \n\nquanti ci sono i report chiusi")

# %%
