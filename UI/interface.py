# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:20:49 2024

@author: akome
"""
# UI/interface.py

import sys
import os
import gradio as gr

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Now import from main.py
from main import generate_response

# Function to handle user input and generate responses
def respond(user_message, chat_history, enhance):
    if chat_history is None:
        chat_history = []
    # Generate the assistant's response
    assistant_response = generate_response(user_message, history=chat_history, enhance=enhance)

    # Check if assistant_response is a dictionary (i.e., when enhance=True)
    if isinstance(assistant_response, dict):
        # Extract the 'final_answer' to display
        assistant_reply = assistant_response.get('final_answer', '')
    else:
        # Use the assistant_response directly
        assistant_reply = assistant_response

    # Append the user message and assistant response to the chat history
    chat_history.append((user_message, assistant_reply))
    return "", chat_history

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# ESUR Guidelines Chatbot")

    chatbot = gr.Chatbot()

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type your message here...",
            label="Your Message",
            lines=2,
            elem_id="user_message"
        )
        enhance_checkbox = gr.Checkbox(label="Enhance Answer", value=False)
        send_button = gr.Button("Send")

    clear = gr.Button("Clear")

    # Connect the components
    # When the user clicks the send button, pass the 'enhance' value from the checkbox
    send_button.click(respond, [msg, chatbot, enhance_checkbox], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()
