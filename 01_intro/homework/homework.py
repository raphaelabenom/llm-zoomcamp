
# %%
import tiktoken
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
import requests 
import minsearch
import json

# %%
# Downloading the documents.json file
docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in tqdm(documents_raw):
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)
        
#%%

documents[0]

#%%

es_client = Elasticsearch('http://localhost:9200') 

es_client.info()

# %%

# Index in elastic search is similar to a table in a database

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} 
        }
    }
}

index_name = "course-questions-homework"

es_client.indices.create(index=index_name, body=index_settings)
# %%

# Indexing documents in Elasticsearch
for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)

# %%
def elastic_search(query):
    search_query = {
        "size": 3, # first 3 results
        "query": {
            "bool": { # bool is used to combine multiple queries
                "must": { # must is like an AND clause in SQL
                    "multi_match": { # multi_match is used to search in multiple fields
                        "query": query, # search query
                        "fields": ["question^4", "text"], # fields to search, with question having higher weight with ^3. Meaning it is 3 times more important than the other fields
                        "type": "best_fields" # best_fields means that the score of the best matching field will be used
                    }
                },
                "filter": { # filter by course, is like a WHERE clause in SQL
                    "term": {
                        "course": "machine-learning-zoomcamp" # filter by course name
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source']) # hit['_source'] contains the document hit['_source'] and hit['_score'] contains the score of the document in the search results
    
    return result_docs

# %%
# Q3
query = "How do I execute a command in a running docker container?"

search = elastic_search(query)
print(search[0])

# %%
#Q4
query = "How do I execute a command in a running docker container?"

search = elastic_search(query)
print(search[0:3])

# %%
def build_prompt(question, search):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
    """.strip()

    template = "question: {question}\ntext: {text}".strip()
    
    context = "\n\n".join(
        template.format(question=doc['question'], text=doc['text'])
        for doc in search
    )
    
    prompt = prompt_template.format(question=question, context=context)
    print("Length of the Prompt:", len(prompt))
    
    return prompt

# %%

formatted_prompt = build_prompt(query, search)

formatted_prompt


#%%
# Q6
encoding = tiktoken.encoding_for_model("gpt-4o")
len(encoding.encode(formatted_prompt))