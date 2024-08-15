
import base64
import io
import shutil
from PIL import Image as PILImage
import os
from openai import OpenAI
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Image
import requests
from app.core.config import settings
from app.helpers.file_parsing.image_description import generate_image_description
from app.helpers.file_parsing.clean_page_content import clean_page_content
from app.helpers.file_parsing.generate_chunk_summary import generate_summary
from app.helpers.qdrant_functions import upload_to_qdrant, make_collection
from app.helpers.semantic_chunk import create_semantic_chunks_80

# def process_pdf(file_content: bytes, file_id: str, file_url: str):
    
#     temp_pdf_path = f"temp_{file_id}.pdf"

#     try:
        
#         with open(temp_pdf_path, "wb") as temp_file:
#             temp_file.write(file_content)

#         elements = partition_pdf(
#             filename=temp_pdf_path,
#             strategy="hi_res",
#             extract_images_in_pdf=True,
#             infer_table_structure=True,
#             model_name="yolox"
#         )

#         total_pages = max(el.metadata.page_number for el in elements)
#         content_parts = []
#         current_page = 0

#         for el in elements:
#             if el.metadata.page_number != current_page:
#                 if current_page > 0:
                    
#                     update_file_status(file_id, f"{current_page}/{total_pages}")
#                 current_page = el.metadata.page_number

#             if isinstance(el, Image):
#                 image_description = process_image(el)
#                 content_parts.append(f"[Image Description: {image_description}]\n")
#             elif hasattr(el, "text"):
#                 content_parts.append(clean_page_content(el.text))

#         update_file_status(file_id, f"{total_pages}/{total_pages}")


#         combined_content = "\n".join(content_parts)
#         save_content_to_file(combined_content, f"processed_{file_id}.txt")

#         update_file_status(file_id, "Completed")

#     except Exception as e:
#         print(f"Error processing PDF: {e}")
#         update_file_status(file_id, "Failed")

#     finally:
#         if os.path.exists(temp_pdf_path):
#             os.remove(temp_pdf_path)

def process_pdf(file_content: bytes, file_id: str, file_url:str, file_name:str):
    temp_pdf_path = f"temp_{file_id}.pdf"
    try:
        make_collection(str(settings.COLLECTION_NAME_RISK_MANAGEMENT))
        with open(temp_pdf_path, "wb") as temp_file:
            temp_file.write(file_content)
        elements = partition_pdf(
            filename=temp_pdf_path,
            strategy="hi_res",
            extract_images_in_pdf=True,
            infer_table_structure=True,
            model_name="yolox"
        )
        total_pages = max(el.metadata.page_number for el in elements)
        content_parts = []  # Declare content_parts here
        current_page = 0
        for el in elements:
            if el.metadata.page_number != current_page:
                if current_page > 0:
                    update_file_status(file_id, f"{current_page}/{total_pages}")
                    page_content = "\n".join(content_parts)
                    cleaned_page_content = clean_page_content(page_content)
                    
                    semantic_chunks = create_semantic_chunks_80(cleaned_page_content)
                    
                    summaries = generate_summary(semantic_chunks)
                    
                    upload_to_qdrant(file_id, file_url,file_name, str(current_page), semantic_chunks, summaries, str(settings.COLLECTION_NAME_RISK_MANAGEMENT))
                   
                    content_parts.clear()
                current_page = el.metadata.page_number

            if isinstance(el, Image):
                image_description = process_image(el)
                content_parts.append(f"[Image Description: {image_description}]\n")
            elif hasattr(el, "text"):
                content_parts.append(el.text)

        # Process the content for the last page
        update_file_status(file_id, f"{total_pages}/{total_pages}")
        page_content = "\n".join(content_parts)
        cleaned_page_content = clean_page_content(page_content)
        semantic_chunks = create_semantic_chunks_80(cleaned_page_content)
        summaries = generate_summary(semantic_chunks)

        upload_to_qdrant(file_id,file_url,file_name, str(current_page), semantic_chunks, summaries, str(settings.COLLECTION_NAME_RISK_MANAGEMENT))

        update_file_status(file_id, "Completed")
    except Exception as e:
        print(f"Error processing PDF: {e}")
        update_file_status(file_id, "Failed")
        # here you may actually call the delete qdrant function and delete all the points. But I would like to keep the partial results
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

        # Deleting the 'figures' folder. It is created temporarily - I donno whether it impacts multiple background file processing
        figures_folder = f"figures"
        if os.path.exists(figures_folder):
            shutil.rmtree(figures_folder)

def process_image(image_element):
    try:
        # # Debug: Print the attributes of image_element and its metadata
        # print("Image element attributes:", dir(image_element))
        # print("Image element metadata attributes:", dir(image_element.metadata))
        
        # I am Trying different possible attributes for image data
        image_data = None
        if hasattr(image_element, 'image'):
            image_data = image_element.image
        elif hasattr(image_element.metadata, 'image'):
            image_data = image_element.metadata.image
        elif hasattr(image_element.metadata, 'image_path'):
            with open(image_element.metadata.image_path, "rb") as img_file:
                image_data = img_file.read()

        if image_data is None:
            print("Unable to find image data. Skipping image processing.")
            return "[Image data not found]"
        
        base64_image = base64.b64encode(image_data).decode('utf-8')

        
        image_description = generate_image_description(base64_image)

        return image_description

    except Exception as e:
        print(f"Error processing image: {e}")
        return "[Image processing failed]"


def save_content_to_file(content, filename):
    try:
        with open(filename, "w", encoding="utf-8") as text_file:
            text_file.write(content)
        print(f"Content saved to {filename}")
    except Exception as e:
        print(f"Error saving content to file: {e}")

def update_file_status(file_id: str, status: str):
    
    update_url = f"{settings.BASE_URL}/api/v1/files/{file_id}"
    response = requests.put(update_url, json={"status": status})
    if response.status_code != 200:
        print(f"Failed to update file status: {response.text}")