import os
import logging
from typing import List

import boto3
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import multiprocessing
from scipy.ndimage import rotate
from goblintools.config import OCRConfig
from goblintools.retry import retry_with_backoff

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self, config: OCRConfig):
        self.config = config
        self._textract_client = None
        # Fall back to local OCR when use_aws=True but credentials are missing
        if config.use_aws and (not config.aws_access_key or not config.aws_secret_key):
            logger.warning(
                "AWS credentials not found; falling back to local Tesseract OCR. "
                "Provide aws_access_key and aws_secret_key in OCRConfig to use AWS Textract."
            )
            self._use_aws_effective = False
        else:
            self._use_aws_effective = config.use_aws

    @property
    def use_aws(self) -> bool:
        """Whether AWS Textract is effectively being used (False when credentials missing)."""
        return self._use_aws_effective

    @property
    def textract_client(self):
        """Lazy-loaded AWS Textract client"""
        if self._textract_client is None and self._use_aws_effective:
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

    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    def _process_page_aws(self, image):
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()

        try:
            response = self.textract_client.detect_document_text(Document={'Bytes': img_bytes})
            return '\n'.join(item['Text'] for item in response['Blocks'] if item['BlockType'] == 'LINE')
        except Exception as e:
            logger.exception(f"Error during AWS Textract processing: {e}")
            return ""

    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
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

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            images = convert_from_path(pdf_path)
        except Exception as e:
            logger.exception(f"Error converting PDF to images: {e}")
            return ""

        if self._use_aws_effective:
            extracted_texts = []
            for image in images:
                text = self._process_page_aws(np.array(image))
                extracted_texts.append(text if text else "")
            return ' '.join(extracted_texts).strip()
        else:
            n_workers = min(multiprocessing.cpu_count(), len(images))
            with multiprocessing.Pool(processes=n_workers) as pool:
                extracted_text = pool.map(self._process_page_local, images)
            return ' '.join(extracted_text).strip()
    
    def extract_text_from_pdf_by_pages(self, pdf_path: str) -> List[str]:
        """Extract text from PDF returning a list of pages"""
        try:
            images = convert_from_path(pdf_path)
        except Exception as e:
            logger.exception(f"Error converting PDF to images: {e}")
            return []

        if self._use_aws_effective:
            extracted_texts = []
            for image in images:
                text = self._process_page_aws(np.array(image))
                extracted_texts.append(text if text else "")
            return extracted_texts
        else:
            n_workers = min(multiprocessing.cpu_count(), len(images))
            with multiprocessing.Pool(processes=n_workers) as pool:
                extracted_text = pool.map(self._process_page_local, images)
            return [text if text else "" for text in extracted_text]
