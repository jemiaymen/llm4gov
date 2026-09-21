#%%
from pypdf import PdfReader
import chromadb
import ollama

PDF_PATH = "data/قانون-عدد-112-لسنة-1983-المؤرخ-في-12-ديسمبر-1983.pdf"
EMBEDDING_MODEL = "bge-m3"
MODEL= "qwen3:4b"
#%%



reader = PdfReader(PDF_PATH)

documents = []
metadatas = []
ids = []


chunk_id = 0
for page_num, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        # Découpage simple par paragraphe/bloc pour conserver les articles intacts
        paragraphs = text.split("\n\n")
        for para in paragraphs:
            cleaned_para = para.strip()
            if len(cleaned_para) > 50:  # Filtrer les fragments trop petits
                documents.append(cleaned_para)
                metadatas.append({"page": page_num + 1})
                ids.append(f"doc_chunk_{chunk_id}")
                chunk_id += 1

print(f"Nombre de segments extraits du PDF : {len(documents)}")

# 2. Génération des Embeddings & stockage dans ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="loi_fonction_publique_ar")

# Fonction pour obtenir des vector embeddings 
def get_embedding(text: str) -> list[float]:
    response = ollama.embed(
        model= EMBEDDING_MODEL,
        input=text
    )

    return response['embeddings'][0]

print("Indexation des segments dans la base vectorielle...")
# Génération et insertion par lots
embeddings = [get_embedding(doc) for doc in documents]

collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
print("Indexation terminée !")

#%%

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="loi_fonction_publique_ar")

def get_embedding(text: str) -> list[float]:
    response = ollama.embed(
        model= EMBEDDING_MODEL,
        input=text
    )

    return response['embeddings'][0]

def repondre_question_rag(question: str) -> str:

    query_embedding = get_embedding(question)

    

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print(f'Result with embedding : {results}')


    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    print(f'Result with text : {results}')


    retrieved_docs = results["documents"][0]
    context = "\n\n---\n\n".join(retrieved_docs)

    print(context)

    

    prompt = f"""أنت مساعد قانوني متخصص في القانون الإداري التونسي. أجب عن السؤال بناءً **فقط حصرياً** على مقتطفات النص أدناه. إذا لم تجد الإجابة هناك، قل ببساطة إن المعلومة غير متوفرة في هذه الوثيقة.

        السياق القانوني المستخرج من ملف الـ PDF:
        {context}

        السؤال: {question}

        الإجابة:"""
    

    response = ollama.chat(model='qwen3:4b',
                           messages=[
                                {
                                    'role': 'user',
                                    'content': prompt,
                                }],
                            options={'temperature': 0.2}
                        )
    

    return response['message']['content']

# 4. مثال على الاستخدام
question = "ما هي شروط عطلة بعث مؤسسة؟"
print(f"\nالسؤال: {question}\n")

reponse = repondre_question_rag(question)
print("إجابة نظام RAG:")
print(reponse)


## https://index.jort.tn/
## https://lake.jort.tn/journal-officiel/ar/2026/001.pdf
## https://lake.jort.tn/journal-officiel/fr/2025/156.pdf

## https://ocr.jort.tn/journal-officiel/fr/2025/156.md
# %%
