from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(vector_store, llm):
    """
    Creates the RAG chain using LCEL.
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    system_prompt = (
        "You are an expert assistant for answering questions about the provided PDF document. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    print(f"DEBUG: create_rag_chain called with llm={type(llm)}")

    from langchain_core.runnables import RunnableLambda
    
    # Imperative RAG function to bypass LCEL construction issues
    def rag_implementation(input_dict):
        query = input_dict["input"]
        
        # Retrieve
        print(f"DEBUG: Retrieving for query: {query}")
        docs = retriever.invoke(query)
        context = format_docs(docs)
        
        # Generator
        print(f"DEBUG: Generating answer")
        prompt_val = prompt.invoke({"context": context, "input": query})
        response_msg = llm.invoke(prompt_val)
        
        return StrOutputParser().invoke(response_msg)

    rag_chain = RunnableLambda(rag_implementation)
    
    return rag_chain
