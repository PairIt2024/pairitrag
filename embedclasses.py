import os 
import dbconfig
import pineconeconfig
import openai
import re

def embed_classes_and_store():
    try:
        collection = dbconfig.connectToDB()

        #Select the Pinecone index
        pc = pineconeconfig.connectToPinecone()
        index = pc.Index("pairitragv2")
        # Get all classes from the database
        cursor = collection.find({})

        #Iiterate over each section and embed the entire section
        for document in cursor:

            # Get the document ID as the Pinecone vector ID
            vector_id = str(document['_id'])

            # Check if the vector already exists in Pinecone
            result = index.fetch(ids=[vector_id])

            
            course_code, section_number = split_section(document['section'])
            full_days = convert_days_abbreviation(document['days'])
            # Combine relevant fields into the class data
            class_data = f"Course: {document['course_title']}, Course Code: {course_code}, " \
                         f"Section: {section_number}, Instructor: {document['instructor']}, " \
                         f"Days: {full_days}, Times: {document['times']}, " \
                         f"Class Type: {document['class_type']}, Location: {document['location']}"
            
            # Add metadata along with the class data
            metadata = {
                "course_title": document["course_title"],
                "course_code": course_code,  # Store the split course code
                "section_number": section_number,  # Store the split section number
                "instructor": document["instructor"],
                "days": full_days,  # Store converted full day names
                "times": document['times'],  # Add times
                "class_type": document['class_type'],  # Add class type (e.g., Lecture or Lab)
                "location": document['location']  # Add location
            }

            response = openai.embeddings.create(
                model="text-embedding-3-small", 
                input=[class_data]  # The input must be a list of strings
            )            

            embedding = response.data[0].embedding
            print(embedding)
            index.upsert(vectors=[
                {
                    "id": str(document['_id']),
                    "values": embedding,
                    "metadata": metadata  
                }
            ])    
    except Exception as e:
        print(f"Error embedding classes: {e}")
        return None

def split_section(section_str):
    # Use regular expression to capture the course and section number separately
    match = re.match(r"([A-Za-z0-9\s]+)\s\((Section\s\d+)\)", section_str)
    
    if match:
        course_code = match.group(1)  # e.g., "AAS 1"
        section_number = match.group(2)  # e.g., "Section 03"
        return course_code, section_number
    else:
        return section_str, "Unknown Section"  # Return as-is if not in the expected format


def convert_days_abbreviation(days_abbr):
    day_map = {
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "R": "Thursday",
        "F": "Friday",
        "S": "Saturday",
        "U": "Sunday"
    }
    return ' and '.join([day_map[char] for char in days_abbr if char in day_map])

if __name__ == "__main__":
    embed_classes_and_store()