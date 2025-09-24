#!/usr/bin/env python3

from goblintools import TextExtractor

def test_ocr_metadata():
    # Initialize extractor with OCR enabled
    extractor = TextExtractor(ocr_handler=True)
    
    # Test OCR with metadata
    print("Testing OCR with metadata extraction...")
    result = extractor.extract_from_file("edital1.pdf", include_metadata=True)
    
    if result and result.get("text"):
        print(f"✅ Text extracted: {len(result['text'])} characters")
        print(f"✅ Metadata generated: {len(result['metadata_markdown'])} characters")
        
        # Save results
        with open("ocr_text.txt", "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        with open("ocr_metadata.md", "w", encoding="utf-8") as f:
            f.write(result["metadata_markdown"])
            
        print("✅ Files saved: ocr_text.txt and ocr_metadata.md")
        
        # Show first 200 chars of each
        print(f"\nFirst 200 chars of text:\n{result['text'][:200]}...")
        print(f"\nFirst 500 chars of metadata:\n{result['metadata_markdown'][:500]}...")
        
    else:
        print("❌ No content extracted")

if __name__ == "__main__":
    test_ocr_metadata()