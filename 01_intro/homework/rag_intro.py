# %%
from openai import OpenAI
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
import minsearch
import json

# %%
'wget https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py'

# %%
with open('documents.json', 'rt') as f_in: #rt = read text mode
    docs_raw = json.load(f_in)

docs_raw

# %%
documents = []

for course_dict in docs_raw:
    for doc in course_dict['documents']:
        doc['course'] = course_dict['course']
        documents.append(doc)

documents[0]

# %%
index = minsearch.Index(
    text_fields=["question", "text", "section"],
    keyword_fields=["course"]
)

# %%
# SELECT * WHERE course = 'data-engineering-zoomcamp';

q = 'the course has already started, can I still enroll?'

index.fit(documents)

# %%
def search(query):
    boost = {'question': 3.0, 'section': 0.5}

    results = index.search(
        query=query,
        filter_dict={'course': 'data-engineering-zoomcamp'},
        boost_dict=boost,
        num_results=5
    )

    return results


print(search(q))

# %%
client = OpenAI()

response = client.chat.completions.create(
    model='gpt-4o',
    messages=[{"role": "user", "content": q}]
)

response.choices[0].message.content

# %%
def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

# %%
def llm(prompt):
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# %%
query = 'how do I run kafka?'

def rag(query):
    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer

# %%
rag(query)

# %%
rag('the course has already started, can I still enroll?')

# %%
documents[0]

# %%
# Elasticsearch setup

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

index_name = "course-questions"

es_client.indices.create(index=index_name, body=index_settings)

# %%
documents[0]

# %%
# Indexing documents in Elasticsearch
for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)

# %%
query = "How do I execute a command in a running docker container?"

# %%
def elastic_search(query):
    search_query = {
        "size": 5, # first 5 results
        "query": {
            "bool": { # bool is used to combine multiple queries
                "must": { # must is like an AND clause in SQL
                    "multi_match": { # multi_match is used to search in multiple fields
                        "query": query, # search query
                        "fields": ["question^4", "text", "section"], # fields to search, with question having higher weight with ^3. Meaning it is 3 times more important than the other fields
                        "type": "best_fields" # best_fields means that the score of the best matching field will be used
                    }
                },
                "filter": { # filter by course, is like a WHERE clause in SQL
                    "term": {
                        "course": "data-engineering-zoomcamp" # filter by course name
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_score']) # '_source' contains the document
    
    return result_docs

#%%
# Search in Elasticsearch - printing the score of the search results
search = elastic_search(query)
print(search)

# %%

def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer

rag(query)
# %%
