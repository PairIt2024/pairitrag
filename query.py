import pinecone
import pineconeconfig
import os
import re
import numpy as np
from dotenv import load_dotenv
from process_query import embed_input, pass_pinecone_results_to_openai

load_dotenv()

def query_class(input):
    try:
        #Select the Pinecone index
        pc = pineconeconfig.connectToPinecone()
        index = pc.Index("pairitragv2")

         #Embed the input text
        response = embed_input(input)
        
        results = index.query(vector=[response], top_k=10, include_metadata=True)

        if results['matches'][0]['score'] > 0.4:
            return pass_pinecone_results_to_openai(input, results)
        else:
            print("No matching results found.")
    except Exception as e:
        print(f"{e}")
        return None


# Build a more structured query string to emphasize key parts
def build_emphasized_input(input_text, courses, instructors, emphasized_courses):
    # Prioritize course number and instructor
    course_string = f"Course(s): {', '.join(courses)}"
    instructor_string = f"Instructor(s): {', '.join(instructors)}"
    emphasis_string = f"Emphasized course(s): {', '.join(emphasized_courses)}"

    # Return a combined query with the prioritized fields emphasized
    return f"{course_string}. {instructor_string}. {emphasis_string}. Original input: {input_text}"


def extract_course_and_instructor(input_text):
    # Updated regex to extract course codes with optional section information
    course_pattern = r"\b[A-Za-z]{2,4}\s?\d{2,3}[A-Za-z]?(?:\sSection\s\d+)?\b"
    # Updated regex to extract names (ensuring that "Section" is not matched as a name)
    name_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b"

    # Find all courses and instructors in the input text
    courses = re.findall(course_pattern, input_text)
    # Filter instructors to ensure "Section" is not included as a name
    instructors = [name for name in re.findall(name_pattern, input_text) if name.lower() != 'section']

    return courses, instructors


if __name__ == "__main__":
    query = "I have CS 157A Section 6 with Narayan Balasubramanian"
    #extracted_input = extract_input(query)
    query_class(query)
    query_class("Computer Science 46A at 1:30pm")
    #query_class("section 3")
    #query_class("engineering reports with Murphey-Wesley")
    #query_class("math 161A")
    #query_class("CS 146 on tuesday thursday at 6:00pm with Rangasayee")
    #query_class("I have class at 3:00pm on Monday and Wednesday")
    #query_class("cmpe 120 at 4:30pm")
    #query_class("I am in Abri’s section 06 class")
   # query_class("I am in section 11 of Physics 50")


    #query_class("CS 157A")
    #query_class("I have CS 146 with Narayan")
    #query_class("Find me classes with Narayan")
    #query_class("Who teaches database management on monday and wednesday")