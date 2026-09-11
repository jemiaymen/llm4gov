#%%
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch,Chroma
from langchain_community.embeddings import OllamaEmbeddings


#%%

import ollama

# 1. Configuration
PDF_PATH = "data/JournalArabe0892026.pdf"
EMBEDDING_MODEL = "bge-m3"      # Excellent for Arabic and multilingual text
LLM_MODEL = "qwen3:4b"            # Or any model fluent in Arabic (e.g., mistral, custom models)
CHUNK_SIZE = 500                # Character length per text chunk

# 2. Extract and Chunk Text from Arabic PDF
def extract_chunks_from_pdf(pdf_path="data/JournalArabe0892026.pdf"):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load_and_split()
    return docs

docs = extract_chunks_from_pdf(PDF_PATH)

print(docs)
#%%
# 3. Generate Embeddings for Document Chunks
print("جاري إنشاء المتجهات نصوص الملف...")

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

store = DocArrayInMemorySearch.from_documents(docs, embedding=embeddings)
store_chroma = Chroma.from_documents(docs, embeddings)
retriever = store.as_retriever()
chroma_store = store_chroma.as_retriever(search_kwargs={"k": 3})
#%%




# 5. Live RAG Chat Query Execution
def ask_rag(user_query,with_chroma=False):
    # Step A: Get relevant context in Arabic
    context = retriever.invoke(user_query)
    print(f"this is context : {context} \n\n" )

    chroma_context = chroma_store.invoke(user_query)

    print(f"this is chroma context : {chroma_context} \n\n" )
    if with_chroma:
        system_prompt = (
                    "أنت مساعد ذكي ومحترف. استخدم السياق المرفق فقط للإجابة على سؤال المستخدم بشكل دقيق ومباشر. "
                    "إذا لم تجد الإجابة في السياق، قل 'لا أملك هذه المعلومة في المستندات المتاحة'.\n\n"
                    " أريد الإجابة بالعربي \n\n"
                    f"السياق المتاح:\n{chroma_context}"
                )
    else:
    
        system_prompt = (
            "أنت مساعد ذكي ومحترف. استخدم السياق المرفق فقط للإجابة على سؤال المستخدم بشكل دقيق ومباشر. "
            "إذا لم تجد الإجابة في السياق، قل 'لا أملك هذه المعلومة في المستندات المتاحة'.\n\n"
            " أريد الإجابة بالعربي \n\n"
            f"السياق المتاح:\n{context}"
        )
    
    # Step C: Use 'from ollama import chat' API 
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        think='low',
        options={"temperature": 0.4} # Lower temperature for more factual retrieval adherence
    )
    
    return response['message']['content']

#%%
arabic_query = "تاريخ فتح مناظرة داخلية بالملــفات للترقــية إلى رتـــبة  قيم عام أول فوق الرتبة بعنوان 2026 "
print(f"\nالسؤال: {arabic_query} \n\n")

answer = ask_rag(arabic_query)
print(f"\nالإجابة:\n{answer}")

# %%
answer = ask_rag(arabic_query,True)
print(f"\nالإجابة:\n{answer}")