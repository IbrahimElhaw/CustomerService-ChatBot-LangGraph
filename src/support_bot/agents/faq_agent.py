from collections.abc import Callable

from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage

from ..prompts import FAQ_PROMPT, NO_INFO_MESSAGE
from ..rag import default_retriever
from ..state import SupportState

Retriever = Callable[[str], list[Document]]

def build_faq_node(llm: BaseChatModel, retriever: Retriever | None = None):
    retriever = retriever or default_retriever

    def faq_node(state: SupportState) -> dict:
        question = str(state["messages"][-1].content)
        docs = retriever(question)
        if not docs:
            return {"messages": [AIMessage(NO_INFO_MESSAGE)]}

        context = "\n\n".join(
            f"[{d.metadata.get('source', '?')}]\n{d.page_content}" for d in docs
        )
        response = llm.invoke(
            [SystemMessage(FAQ_PROMPT.format(context=context)), *state["messages"]]
        )
        sources = sorted({d.metadata.get("source", "?") for d in docs})
        return {"messages": [AIMessage(f"{response.content}\n\nQuellen: {', '.join(sources)}")]}

    return faq_node

