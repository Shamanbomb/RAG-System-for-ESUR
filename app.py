# app.py
import os
import sys
import gradio as gr

# Ensure the directory containing the 'Scripts' module is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))

from main import generate_response

# Initialize an empty list to store the conversation history
history = []

# Gradio interface function with history
def gradio_interface(query, history):
    # Add the new query to the conversation history
    history.append({"role": "user", "content": query})
    
    # Generate the response
    response = generate_response_with_history(history)
    
    # Add the model's response to the history
    history.append({"role": "assistant", "content": response})
    
    # Format the history for display
    formatted_history = []
    for message in history:
        formatted_history.append(f"{message['role']}: {message['content']}")
    
    return response, history, "\n".join(formatted_history)

# Function to generate response using Together API with message history
def generate_response_with_history(history):
    # Combine the history into a single string with roles
    context = ""
    for message in history:
        context += f"{message['role']}: {message['content']}\n"
    
    instructions = (
        "Use the context to answer the question/query to the best of your ability. "
        "Give citations for your answer, if possible using chapters/pages. There is no need to include the references at the end.\n"
    )
    
    # Last message is the current user query
    query = history[-1]["content"]
    input_text = f"{instructions}Context:\n{context}User query: {query}\n"
    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        messages=[{"role": "user", "content": input_text}],
        max_tokens=512
    )
    
    return response.choices[0].message.content

# Create Gradio interface
interface = gr.Interface(
    fn=gradio_interface,
    inputs=[gr.inputs.Textbox(lines=2, placeholder="Enter your query here..."), gr.State([])],
    outputs=["text", "state", "text"],
    title="ESUR-Guidelines",
    description="Ask a question and get a detailed answer with citations."
)

# Launch the interface
if __name__ == "__main__":
    interface.launch()