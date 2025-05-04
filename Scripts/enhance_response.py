# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 09:23:55 2024

@author: akome
"""

# Scripts/enhance_response.py

import os
import sys
import logging
import json
from together import Together

# Import functions from utils.py
from Scripts.utils import retrieve_documents, embed_text

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

setup_logging()

# Initialize Together client
API_KEY = os.environ.get("TOGETHER_API_KEY")
if not API_KEY:
    logging.error("TOGETHER_API_KEY not found in environment variables.")
    sys.exit(1)
client = Together(api_key=API_KEY)

def evaluate_response(question, context, initial_answer):
    """
    Evaluates the initial answer to determine if:
    - The provided context was relevant to answering the question.
    - The question was answered fully.
    - Which context chunks were used in answering the question.
    Returns a dictionary with evaluation results.
    """
    try:
        # Build the prompt for evaluation
        evaluation_prompt = f"""
You are an expert assistant helping to evaluate an answer to a question based on provided context.

Question: {question}

Context:
{context}

Answer:
{initial_answer}

Please analyze the above answer and determine:
1. Was the provided context relevant to answering the question? (Yes/No)
2. Was the question answered fully and correctly? (Yes/No)
3. List the specific context chunks (by their indices) that were used in generating the answer.

Provide your evaluation in the following JSON format and nothing else:
{{
    "context_relevant": "Yes" or "No",
    "question_answered_fully": "Yes" or "No",
    "used_context_chunks": [list of indices]
}}
"""

        # Make the API call
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": evaluation_prompt}],
            max_tokens=512
        )
        if response and response.choices:
            assistant_reply = response.choices[0].message.content.strip()
            logging.debug(f"Evaluation response: {assistant_reply}")
            # Parse the assistant's reply as JSON
            evaluation_result = json.loads(assistant_reply)
            return evaluation_result
        else:
            logging.error("Empty response from the model during evaluation.")
            return None
    except Exception as e:
        logging.error(f"Error in evaluate_response: {e}")
        return None

def find_citations(question, context_chunks, initial_answer):
    """
    Finds exact snippets from the context chunks to cite in the answer.
    Returns the reformulated answer with citations.
    """
    try:
        # Build the prompt for citation
        context_text = "\n\n".join([f"Chunk {i}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        citation_prompt = f"""
You are an assistant that enhances answers by adding exact citations from the provided context chunks.

Question: {question}

Context Chunks:
{context_text}

Answer:
{initial_answer}

Please find the exact snippets from the context chunks that support the answer, and formulate an answer to include these citations. Use verbatim citations.

Provide the enhanced answer with citations.
"""

        # Make the API call
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": citation_prompt}],
            max_tokens=512
        )
        if response and response.choices:
            enhanced_answer = response.choices[0].message.content.strip()
            logging.debug(f"Enhanced answer with citations: {enhanced_answer}")
            return enhanced_answer
        else:
            logging.error("Empty response from the model during citation.")
            return initial_answer
    except Exception as e:
        logging.error(f"Error in find_citations: {e}")
        return initial_answer

def expand_question(question):
    """
    Expands the question by generating relevant keywords or search terms.
    Returns the expanded query.
    """
    try:
        # Build the prompt for expansion
        expansion_prompt = f"""
You are an assistant that improves questions for better information retrieval.

Original Question: {question}

Please generate a list of relevant keywords or search terms related to the question, focusing on where it might appear in the ESUR guidelines. Do not provide generic search terms, but instead focus on key words that might appear in the relevant sections of the ESUR Guidelines on contrast agent.
If the question is formulated poorly, please reformulate it and then provide the expanded query as a string and nothing else in the following format: "Question"+"Keywords". Do not provide any other text.
"""

        # Make the API call
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": expansion_prompt}],
            max_tokens=128
        )
        if response and response.choices:
            expanded_query = response.choices[0].message.content.strip()
            logging.debug(f"Expanded query: {expanded_query}")
            return expanded_query
        else:
            logging.error("Empty response from the model during question expansion.")
            return question
    except Exception as e:
        logging.error(f"Error in expand_question: {e}")
        return question

def enhance_answer(question, context_chunks, initial_answer):
    """
    Main function to enhance the initial answer based on evaluation.
    Returns a dictionary with detailed information.
    """
    result = {
        'original_answer': initial_answer,
        'evaluation': None,
        'final_answer': initial_answer,
        'expanded_keywords': None
    }

    # Combine context chunks into a single string
    context = "\n\n".join([f"Chunk {i}:\n{chunk}" for i, chunk in enumerate(context_chunks)])

    # Step 1: Evaluate the initial answer
    evaluation_result = evaluate_response(question, context, initial_answer)
    result['evaluation'] = evaluation_result

    if not evaluation_result:
        logging.error("Evaluation failed. Returning initial answer.")
        return result

    context_relevant = evaluation_result.get("context_relevant", "No")
    question_answered_fully = evaluation_result.get("question_answered_fully", "No")
    used_context_chunks = evaluation_result.get("used_context_chunks", [])

    if context_relevant == "Yes" and question_answered_fully == "Yes" and used_context_chunks:
        # Step 2A: Find citations and reformulate the answer
        used_indices = [int(idx) for idx in used_context_chunks]
        used_chunks = [context_chunks[i] for i in used_indices if i < len(context_chunks)]
        enhanced_answer = find_citations(question, used_chunks, initial_answer)
        result['final_answer'] = enhanced_answer
    else:
        # Step 2B: Expand the question and retrieve new context
        expanded_query = expand_question(question)
        result['expanded_keywords'] = expanded_query

        # Retrieve new context using the expanded query
        new_context_chunks = retrieve_documents(expanded_query, k=5)
        if not new_context_chunks:
            logging.error("No new context retrieved with expanded query.")
            result['final_answer'] = "I'm sorry, I couldn't find any relevant information to answer your question."
            return result

        # Generate a new answer with the new context
        messages = []
        instructions = (
            "You are an assistant that provides information based on the ESUR guidelines. "
            "Provide clear and concise answers, citing chapters or pages when possible."
        )
        combined_context = " ".join(new_context_chunks)
        max_context_length = 2000  # Adjust based on your model's limits
        context = combined_context[:max_context_length]
        user_content = f"{instructions}\n\nUser query: {question}\n\nContext:\n{context}"
        messages.append({"role": "user", "content": user_content})

        # Generate a new answer
        try:
            response = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
                messages=messages,
                max_tokens=512
            )
            if response and response.choices:
                new_answer = response.choices[0].message.content.strip()
                result['final_answer'] = new_answer
            else:
                logging.error("Empty response from the model during answer generation.")
                result['final_answer'] = "I'm sorry, I couldn't generate a response."
        except Exception as e:
            logging.error(f"Error generating new answer: {e}")
            result['final_answer'] = "I'm sorry, there was an error processing your request."

    return result


