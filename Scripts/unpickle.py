import pickle

# Load the documents.pkl file
with open('documents.pkl', mode='rb') as f:
    data = pickle.load(f)

# Define the output text file
output_file = 'extracted_chunks.txt'

# Write chunks to the file, separating them with paragraphs
with open(output_file, 'w', encoding='utf-8') as f:
    for idx, chunk in enumerate(data, start=1):
        f.write(f"Chunk {idx}:\n{chunk}\n\n{'-' * 50}\n\n")

print(f"Chunks have been successfully written to {output_file}")
