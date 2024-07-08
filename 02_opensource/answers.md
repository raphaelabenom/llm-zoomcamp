# Q1

# 1
docker run -it \
    --rm \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama

# 2
docker exec -it ollama bash

# 3
ollama -v


# Q2

cat /root/.ollama/models/manifests/registry.ollama.ai/library/gemma/2b


# Q3
Output from 10 * 10
Sure, here is the answer to your question: 10 * 10 = 100

# Q4

mkdir ollama_files

docker run -it \
    --rm \
    -v ./ollama_files:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama

docker exec -it ollama ollama pull gemma:2b 

# Linux command
du -h

# Q5

ollama_files/ root/.ollama/


# Q6

304