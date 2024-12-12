import json
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.schema.runnable import RunnableLambda, RunnableParallel
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables.config import RunnableConfig
from loguru import logger
from utils import AppSettings
from utils.aiutils import get_chatmodel

settings = AppSettings.AppSettings()
llm = get_chatmodel()
json_llm = get_chatmodel(use_ollama_json_format=True)


# LLMs
######

### Retrieval Grader

# prompt = PromptTemplate(
#     template="""You are a grader assessing relevance of a retrieved document to a user question. \n
#     Here is the retrieved document: \n\n {document} \n\n
#     Here is the user question: {question} \n
#     If the document contains keywords related to the user question, grade it as relevant. \n
#     It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
#     Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
#     Provide the binary score as a JSON with a single key 'score' and no premable or explanation.""",
#     input_variables=["question", "document"],
# )

retrieval_grader_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing relevance
    of a retrieved document to a user question. If the document contains keywords related to the user question,
    grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
     <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "document"],
)
retrieval_grader = retrieval_grader_prompt | json_llm | JsonOutputParser()


### Generate
def format_document_context(dictonary_docs):
    docs = dictonary_docs.get("context", [])
    if not docs:
        return ""
    try:
        if type(docs[0]) == str:
            rv = "\n------\n".join(docs)
        elif type(docs[0]) == Document:
            rv = "\n----\n".join(doc.page_content for doc in docs)
        else:
            rv = "\n---\n".join(doc["page_content"] for doc in docs)
    except Exception as e:
        logger.error(
            f"Fehler in format_document_context, docs wird unverändert zurückgegeben: {e}"
        )
        rv = dictonary_docs
    return rv


def get_question(json_in):
    return json_in["question"]


# Prompt

# rag_chain_prompt = PromptTemplate(
#     template="""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
#     Use three sentences maximum and keep the answer concise. \n
#     Question: {question}  \n
#     Context: {context}  \n
#     Answer: """,
#     input_variables=["context", "question"],
# )

rag_chain_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> Du bist ein Assistent für Frage-Antwort Aufgaben.
    Beantworte die folgende FRAGE ausschließlich mit dem unten aufgeführten Kontext. Wenn du die Antwort nicht weißt, antworte mit 'Das weiß ich leider nicht'.
    Antworte immer auf Deutsch. Antworte ausführlich und sehr gewissenhaft. <|eot_id|><|start_header_id|>user<|end_header_id|>
    \n ------- \n
    FRAGE: {question}
    \n ------- \n
    Kontext: {context}
    \n ------- \n
    Antwort: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "document"],
)


rag_chain = (
    RunnableParallel(
        {
            "context": RunnableLambda(format_document_context),
            "question": RunnableLambda(get_question),
        }
    )
    | rag_chain_prompt
    | llm
    | StrOutputParser()
)


### Hallucination Grader
hallucination_grader_prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether
    an answer is grounded in / supported by a set of facts. Give a binary 'yes' or 'no' score to indicate
    whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a
    single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the facts:
    \n ------- \n
    {documents}
    \n ------- \n
    Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "documents"],
)
hallucination_grader = hallucination_grader_prompt | json_llm | JsonOutputParser()


### Answer Grader
answer_grader_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an
    answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is
    useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
     <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
    \n ------- \n
    {generation}
    \n ------- \n
    Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "question"],
)
answer_grader = answer_grader_prompt | json_llm | JsonOutputParser()


re_write_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>Du bist ein Frage-Umformulierer, der eine Eingabefrage in eine bessere Version umwandelt, die
     für die Abfrage im Vektorspeicher optimiert ist. Schau dir die ursprüngliche Frage an und formuliere eine bessere Version. Gib ausschliesslich die umformulierte Frage aus.
     Antworte auf deutsch. Sehe dir den Input an und versuche, die zugrunde liegende semantische Absicht und Bedeutung zu erschließen. Ist die Frage sehr speziell,
     formuliere sie etwas allgemeiner ohne dabei wichtige Informationen zu verlieren. Verwende Synonyme.
     <|eot_id|><|start_header_id|>user<|end_header_id|> Hier ist die Eingabefrage:\n{question}\n
     Umformulierte Frage: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)
question_rewriter = re_write_prompt | llm | StrOutputParser()


### History Question Rewriter
contextualize_q_system_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>Du erhältst einen Chatverlauf und die letzte Nutzerfrage,
    die sich möglicherweise auf den Inhalt des Chatverlaufs bezieht. Formuliere die Frage so um, dass sie ohne den Chatverlauf verständlich ist.
    Wichtig: Beantworte die Frage NICHT, sondern formuliere sie falls nötig um oder gib sie unverändert zurück.
    Gib ausschließlich diese Frage zurück.
    Remember: do not answer the question, but rather formulate the question so that it is verifiable without the context of the chat history. Your Output must be a question!
    <|eot_id|><|start_header_id|>user<|end_header_id|>"""

# NOTE: do not use "system" for contextualize_q_system_prompt
# this seemes to be ignored when using llama
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
recreate_chain = contextualize_q_prompt | llm | StrOutputParser()

# Typing extensions: It is highly recommended to import Annotated and TypedDict from typing_extensions instead of typing to ensure consistent behavior across Python versions.
# https://python.langchain.com/docs/how_to/structured_output/
from typing_extensions import Annotated, TypedDict, List


class FurtherQuestions(TypedDict):
    """Further questions."""

    questions: Annotated[List[str], ..., "The list of the generated further questions"]


def further_q_parser(output: any) -> dict:
    try:
        if type(output["questions"]) is list:
            if isinstance(output["questions"][0], str):
                return output
            else:
                return {"questions": [d["value"] for d in output["questions"]]}
        elif isinstance(output["questions"], str):
            return {"questions": json.loads(output["questions"])}
        else:
            raise ValueError("Unexpected output format in further_q_parser")
    except:
        logger.warning(f"Unexpected output format in further_q_parser: {output}")
        return {"questions": []}


further_q_system_prompt = """
    Du erhältst einen Chatverlauf bestehend aus einer Frage und einer generierten Antwort.
    Erstelle 3 weitere Fragen, die den Chatverlauf fortführen könnten.
    """

further_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", further_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", ""),
    ]
)

# Since there is a bug in the passing of the config, ollama_model_name is ignored at json_llm
further_questions_chain = (
    further_q_prompt
    | json_llm.with_structured_output(FurtherQuestions)
    | RunnableLambda(further_q_parser)
)


def create_chain(promptTemplate: PromptTemplate, json_output: bool = False):
    if json_output:
        return promptTemplate | json_llm | JsonOutputParser()
    else:
        return promptTemplate | llm | StrOutputParser()


def patch_config(config: RunnableConfig):
    """Patches the configurable keys in the config by using metadata.
       They are deleted somewhere, so this workaround is:
       Use metadata instead of configurable

    Args:
        config (RunnableConfig): the config to patch
    """
    keys = ["llm", "further_questions", "ollama_model_name", "search_kwargs"]

    for key in keys:
        if key in config.get("metadata", {}):
            config.get("configurable", {})[key] = config.get("metadata", {})[key]
    return config
