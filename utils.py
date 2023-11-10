import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.schema import Document
import pinecone
from pypdf import PdfReader
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain
import numpy as np
import re
import requests
from transformers import BertTokenizerFast, BertLMHeadModel
from transformers import pipeline

#Extract Information from PDF file
def get_pdf_text(filename):
    text = ""
    pdf_ = PdfReader(filename)
    for page in pdf_.pages:
        text += page.extract_text()
    return text



# iterate over files in
# that user uploaded PDF files, one by one

def create_docs(user_file_list, unique_id):
  docs = []
  for filename in user_file_list:

      ext = filename.split(".")[-1]

      # Use TextLoader for .txt files
      if ext == "txt":

          loader = TextLoader(filename)
          doc = loader.load()

      # Use HTMLLoader for .html files
      elif ext == "html":
          loader = UnstructuredHTMLLoader(filename)
          doc = loader.load()

      # Use PDFLoader for .pdf files
      elif ext == "pdf":
          loader = PyPDFLoader(filename)
          doc = loader.load()

      elif ext == "docx":
          loader = Docx2txtLoader(filename)
          doc = loader.load()

      elif ext == "md":
          loader = UnstructuredMarkdownLoader(filename)
          doc = loader.load()
      # Skip other file types
      else:
          continue
      docs.append(Document( page_content= doc[0].page_content , metadata={"name": f"{filename}" , "unique_id":unique_id } ) )

  return docs


# def create_docs(user_pdf_list, unique_id):
#   docs = []
#   for filename in user_pdf_list:
#       docs.append(Document( page_content= get_pdf_text(filename), metadata={"name": f"{filename}" , "unique_id":unique_id } ) )
#       docs.append(get_pdf_text(filename))
      
#   return docs



#Create embeddings instance
def create_embeddings_load_data():
    #embeddings = OpenAIEmbeddings()
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") #  384
    return embeddings


#Function to push data to Vector Store - Pinecone here
def push_to_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings,docs):

    pinecone.init(
    api_key=pinecone_apikey,
    environment=pinecone_environment
    )
    print("done......2")
    Pinecone.from_documents(docs, embeddings, index_name=pinecone_index_name)
    


#Function to pull infrmation from Vector Store - Pinecone here
def pull_from_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings):

    pinecone.init(
    api_key=pinecone_apikey,
    environment=pinecone_environment
    )

    index_name = pinecone_index_name

    index = Pinecone.from_existing_index(index_name, embeddings)
    return index


def similar_docs_hf(query, final_docs_list, k):

    HF_KEY = "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"
    
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

    payload = {
        "inputs": {
            "source_sentence": query, # query
            "sentences": final_docs_list
        }
      }
    response = requests.post(API_URL, headers=headers, json=payload)

    score_list = response.json()

    
    pairs = list(zip( score_list , final_docs_list))

    # Sort the pairs in descending order of the first element of each pair
    pairs.sort(key=lambda x: x[0], reverse=True)

    # Unzip the pairs back into two lists
    score_list , final_docs_list = zip(*pairs)
    # sorted_list[:k] ,
    return    score_list , final_docs_list 


#Function to help us get relavant documents from vector store - based on user input
def similar_docs(query,k,pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings,unique_id):

    pinecone.init(
    api_key=pinecone_apikey,
    environment=pinecone_environment
    )

    index_name = pinecone_index_name

    index = pull_from_pinecone(pinecone_apikey,pinecone_environment,index_name,embeddings)
    similar_docs = index.similarity_search_with_score(query, int(k),{"unique_id":unique_id})
    #print(similar_docs)
    return similar_docs


def get_score(relevant_docs):
  scores = []
  for doc in relevant_docs:
      scores.append(doc[1])

  return scores


def metadata_filename( document ) : 
   
   names = [ ]
   for doc in document: 
    
        text = str(doc[0].metadata["name"] )
        pattern = r"name=\'(.*?)\'"
        matches = re.findall(pattern, text)
        names.append(matches) 

   return names

def docs_content(relevant_docs):
    content = [] 
    for doc in relevant_docs:    
        content.append(doc[0].page_content)

    return content
      
def docs_summary(relevant_docs ):
    documents = []
    summary = [ ] 

    for doc in relevant_docs:     
        documents.append(doc[0].page_content)

    for document in documents :
           summary.append( document )
    return summary


def get_summary_hf(target) :


    # Specify the model name
    model_name = "bert-base-uncased"

    # Load the BERT tokenizer and model
    tokenizer = BertTokenizerFast.from_pretrained(model_name)
    model = BertLMHeadModel.from_pretrained(model_name)

    # Initialize the summarization pipeline
    summarizer = pipeline('summarization', model=model, tokenizer=tokenizer)

    # Use the pipeline to summarize the text
    summary = summarizer(str(target), max_length=150, min_length=25, do_sample=False)

    return summary


# def get_summary_hf( document ):

#   HF_KEY = "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"
#   API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
#   headers = {"Authorization": f"Bearer {HF_KEY}"}
#   payload = {
#         "inputs": {
#             "inputs":  document ,
#              "parameters": {"do_sample": False}
#         }
#       }
    
#   response = requests.post(API_URL, headers=headers, json=payload)
#   return response.json()

# Helps us get the summary of a document


def get_summary(current_doc):

    llm = OpenAI(temperature=0)
    # llm = HuggingFaceHub(repo_id="bigscience/bloom", model_kwargs={"temperature":1e-10})
    chain = load_summarize_chain(llm, chain_type="map_reduce") 
    summary = chain.run([current_doc])

    return summary 


    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #     {"role": "system", "content": f"{current_doc}" },
    #     {"role": "user", "content": "Summarize the following text: '{text_to_summarize}'"},
    # ])

    # return response['choices'][0]['message']['content'] 
    # 
