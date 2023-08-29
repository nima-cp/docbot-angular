# %%

from typing import Any, Dict, List
import openai


openai.api_key = OPENAI_API_KEY

# %%

gpt_model = "gpt-3.5-turbo"


# instruction = """report: \n\n{reports}\n\nCronologia della chat:\n\n{chat_history} \n\nUtente: {user}\n\n assistente:"""
instruction = (
    """Cronologia della chat:\n\n{chat_history} \n\nUtente: {user}\n\n assistente:"""
)
system_prompt = """Sei un utile assistente italiano. Il tuo compito è aiutare gli utenti di un sito di Whistleblowing a gestire le attività legate alle segnalazioni.
Identificazione e classificazione dei report in base al loro stato (es. "nuovo", "in corso", "completato", "archiviato"), chi ha creato il report, chi ne è responsabile e quando è la data di scadenza.

Se non sei sicuro, dì non lo so.
Rispondi con risposte brevi e precise, senza alcuna elaborazione in italiano.
"""

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"


def get_prompt(instruction, new_system_prompt):
    SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    return prompt_template


template = get_prompt(instruction, system_prompt)


messages = [
    {"role": "system", "content": template},
]

# %%


def chat(question):
    messages.append({"role": "user", "content": question})
    chat = openai.ChatCompletion.create(model=gpt_model, messages=messages)
    return chat


# %%
reply = chat("quanti sono le segnalazioni chiusi?")

print(f"ChatGPT: {reply}")
messages.append({"role": "assistant", "content": reply})
# %%
