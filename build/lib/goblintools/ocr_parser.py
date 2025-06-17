import os
import logging
import boto3
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

textract_client = boto3.client(
    'textract',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

def extract_text_from_image_aws(image):
    _, img_encoded = cv2.imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()

    try:
        response = textract_client.detect_document_text(Document={'Bytes': img_bytes})
        return '\n'.join(item['Text'] for item in response['Blocks'] if item['BlockType'] == 'LINE')
    except Exception as e:
        logger.exception(f"Error occurred during Textract text extraction: {e}")
        return ""

def extract_text_from_pdf_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        logger.exception(f"Error occurred while converting PDF to images: {e}")
        return ""

    extracted_texts = []
    for image in images:
        text = extract_text_from_image_aws(np.array(image))
        if text:
            extracted_texts.append(text)

    return ' '.join(extracted_texts).strip()
