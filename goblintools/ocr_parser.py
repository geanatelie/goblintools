import os
import logging
import boto3
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import multiprocessing
from scipy.ndimage import rotate
from goblintools.config import OCRConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self, config: OCRConfig):
        self.config = config
        self._textract_client = None
    
    @property
    def textract_client(self):
        """Lazy-loaded AWS Textract client"""
        if self._textract_client is None and self.config.use_aws:
            if not self.config.aws_access_key or not self.config.aws_secret_key:
                raise ValueError("AWS credentials must be provided if use_aws is True.")
            try:
                self._textract_client = boto3.client(
                    'textract',
                    region_name=self.config.aws_region,
                    aws_access_key_id=self.config.aws_access_key,
                    aws_secret_access_key=self.config.aws_secret_key
                )
            except Exception as e:
                logger.error(f"Failed to initialize AWS Textract client: {e}")
                raise
        return self._textract_client

    def _process_page_aws(self, image):
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()

        try:
            response = self.textract_client.detect_document_text(Document={'Bytes': img_bytes})
            return '\n'.join(item['Text'] for item in response['Blocks'] if item['BlockType'] == 'LINE')
        except Exception as e:
            logger.exception(f"Error during AWS Textract processing: {e}")
            return ""

    def _process_page_local(self, image):
        image = np.array(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        def determine_score(arr, angle):
            data = rotate(arr, angle, reshape=False, order=0)
            histogram = np.sum(data, axis=1, dtype=float)
            return np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)

        delta = 1
        limit = 5
        scores = [determine_score(thresh, angle) for angle in range(-limit, limit + delta, delta)]
        best_angle = (np.argmax(scores) - limit) * delta

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
        corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return pytesseract.image_to_string(corrected, lang=self.config.tesseract_lang)

    def extract_text_from_pdf(self, pdf_path):
        try:
            images = convert_from_path(pdf_path)
        except Exception as e:
            logger.exception(f"Error converting PDF to images: {e}")
            return ""

        if self.config.use_aws:
            extracted_texts = []
            for image in images:
                text = self._process_page_aws(np.array(image))
                if text:
                    extracted_texts.append(text)
            return ' '.join(extracted_texts).strip()
        else:
            with multiprocessing.Pool() as pool:
                extracted_text = pool.map(self._process_page_local, images)
            return ' '.join(extracted_text).strip()
        
