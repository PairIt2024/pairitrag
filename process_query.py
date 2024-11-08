from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

def embed_input(input_text):
    response = client.embeddings.create(
                model="text-embedding-3-small", 
                input=[input_text]  # The input must be a list of strings
            ).data[0].embedding
    return response 

def extract_input(input_text):
    # Extract the class name from the user input
    print(f"Extract the course name, instructor, and type of class (e.g., lab or lecture) from the following query: '{input_text}'")
    prompt = f"Extract the course name, instructor, and type of class (e.g., lab or lecture) from the following query: '{input_text}'"
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an assistant that extracts key information from user queries."},
        {"role": "user", "content": f"Extract the course name, instructor, and type of class (e.g., lab or lecture) from the following query: '{input_text}'"}
    ],
    max_tokens=100)    
    extracted_input = response.choices[0].message.content.strip()
    print(f"Extracted input: {extracted_input}")
    return extracted_input

def pass_pinecone_results_to_openai(original_query, pinecone_results):
    # Format the Pinecone results into a user-friendly string for OpenAI to process
    result_string = ""
    for i, match in enumerate(pinecone_results['matches']):
        metadata = match['metadata']
        #result_string += f"{i+1}. Course: {metadata['course_title']}, Instructor: {metadata['instructor']}, Section: {metadata.get('section', 'N/A')}, Score: {match['score']}\n"
        result_string += f"{i+1}. ID: {match['id']}, Course: {metadata['course_title']}, Instructor: {metadata['instructor']}, Section: {metadata.get('section_number', 'N/A')}, Score: {match['score']}\n"    
    # Pass this to OpenAI for further refinement
    print(result_string)
    prompt = (
        f"Original query: '{original_query}'\n\n"
        f"Based on the user's query, here are some possible course matches from Pinecone:\n{result_string}\n\n"
        "Your task is to rank these courses in order of relevance to the original query. Consider details such as the course title, "
        "instructor, section number, and any other relevant information. Output a ranked list of the top 10 matches, focus on the split between Section and courses example, CS46A is different than CS46B"
        "and provide the reasoning for each selection based on the query. The output should be the list of IDs of the most relevant courses."
    )    
    # Call OpenAI's ChatCompletion endpoint to analyze the results and pick the most relevant
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that matches the user's query with the most relevant course based on the provided options. Do not provide new course options. Return only a list of top 10 IDs of the most relevant course."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    # Extract the relevant response from OpenAI
    final_result = response.choices[0].message.content.strip()

    # Print and return the final result
    print(f"Final result from OpenAI: {final_result}")
    print("Right before returning final result")
    return final_result