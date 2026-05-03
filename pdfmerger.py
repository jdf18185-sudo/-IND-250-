import sys
import os
from pathlib import Path
from PyPDF2 import PdfMerger


def main():
    # Step 1 & 2: Read output filename from command line or error
    if len(sys.argv) < 2:
        print("Error: Merge file name not specified. Usage: python pdfmerger.py filename")
        sys.exit(1)
    
    output_filename = sys.argv[1]
    output_pdf = f"{output_filename}.pdf"
    
    # Step 3: Initialize merger object
    merger = PdfMerger()
    
    # Step 4 & 5: Retrieve and filter PDF files in current directory
    pdf_files = []
    for file in os.listdir('.'):
        if file.endswith('.pdf') and file != output_pdf:
            pdf_files.append(file)
    
    # Step 6: Sort alphabetically
    pdf_files.sort()
    
    # Step 7: Report findings
    print(f"PDF files found: {len(pdf_files)}")
    if pdf_files:
        print("List:")
        for pdf_file in pdf_files:
            print(pdf_file)
    
    # Step 8: Prompt user to continue
    if not pdf_files:
        print("\nNo PDF files found to merge.")
        sys.exit(0)
    
    user_input = input("\nContinue (y/n): ").strip().lower()
    if user_input != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Step 9: Append each PDF to merger
    for pdf_file in pdf_files:
        try:
            merger.append(pdf_file)
            print(f"Added: {pdf_file}")
        except Exception as e:
            print(f"Error adding {pdf_file}: {e}")
    
    # Step 10: Export/Save the merged PDF
    try:
        merger.write(output_pdf)
        merger.close()
        print(f"\nMerged PDF saved as: {output_pdf}")
    except Exception as e:
        print(f"Error saving merged PDF: {e}")
        sys.exit(1)
    
    # Bonus Step: Extract text from merged PDF and save as .txt file
    extract_text = input("\nExtract text from merged PDF? (y/n): ").strip().lower()
    if extract_text == 'y':
        try:
            from PyPDF2 import PdfReader
            output_txt = f"{output_filename}.txt"
            
            reader = PdfReader(output_pdf)
            full_text = ""
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text += f"\n--- Page {page_num + 1} ---\n"
                full_text += text
            
            with open(output_txt, 'w', encoding='utf-8') as txt_file:
                txt_file.write(full_text)
            
            print(f"Text extracted and saved as: {output_txt}")
        except Exception as e:
            print(f"Error extracting text: {e}")


if __name__ == "__main__":
    main()
