import os
import pandas as pd
import pdfplumber
from concurrent.futures import ProcessPoolExecutor
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(filename="processing.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_pdf_content(pdf_path):
    """Extracts text and tables from a PDF file."""
    content = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                text = page.extract_text()
                if text:
                    content.append({"Type": "Text", "Page": page_num, "Content": text})
                
                # Extract tables, if any
                tables = page.extract_tables()
                for table in tables:
                    df_table = pd.DataFrame(table)
                    content.append({"Type": "Table", "Page": page_num, "Content": df_table})
    except Exception as e:
        logging.error(f"Error extracting content from {pdf_path}: {e}")
    return content

def process_single_pdf(pdf_file, pdf_folder, output_folder):
    """Processes a single PDF and saves its content to a single Excel sheet."""
    try:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        extracted_content = extract_pdf_content(pdf_path)
        output_path = os.path.join(output_folder, f"{pdf_file[:-4]}.xlsx")
        
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            row_data = []
            for item in extracted_content:
                if item["Type"] == "Text":
                    # Split text into lines
                    lines = item["Content"].split("\n")
                    for line in lines:
                        # Check if the line is a header (e.g., all uppercase or ends with a colon)
                        if line.isupper() or line.strip().endswith(":"):
                            row_data.append([line.strip()])  # Add header in its own row
                        else:
                            # Split paragraphs into multiple cells if needed
                            cells = [cell.strip() for cell in line.replace("○", "").replace("\t", " ").split(",") if cell.strip()]
                            row_data.append(cells if cells else [line.strip()])  # Add paragraph or line
                elif item["Type"] == "Table":
                    # Append table rows directly
                    table_data = item["Content"].values.tolist()
                    row_data.extend(table_data)  # Add table rows as-is
            
            # Create a DataFrame for row data
            max_columns = max(len(row) for row in row_data)  # Handle variable column counts
            formatted_data = pd.DataFrame(row_data, columns=[f"Column_{i+1}" for i in range(max_columns)])
            formatted_data.to_excel(writer, sheet_name="Extracted_Content", index=False, header=False)
        
        logging.info(f"Processed {pdf_file} into {output_path}")
    except Exception as e:
        logging.error(f"Error processing {pdf_file}: {e}")

def process_pdf_wrapper(args):
    """Wrapper function to unpack arguments for process_single_pdf."""
    pdf, pdf_folder, output_folder = args
    process_single_pdf(pdf, pdf_folder, output_folder)

def process_pdfs_parallel(pdf_folder, output_folder):
    """Processes all PDFs in a folder using parallel processing."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    tasks = [(pdf, pdf_folder, output_folder) for pdf in pdf_files]
    
    with ProcessPoolExecutor() as executor:
        list(tqdm(executor.map(process_pdf_wrapper, tasks), total=len(pdf_files)))

    print(f"All PDFs processed. Files saved to {output_folder}")

# Example usage
if __name__ == "__main__":
    pdf_folder = r"C:\Users\Ezelda\Desktop\Freelancer\PDF_examples"
    output_folder = r"C:\Users\Ezelda\Desktop\Freelancer\Excel_output_examples"
    process_pdfs_parallel(pdf_folder, output_folder)