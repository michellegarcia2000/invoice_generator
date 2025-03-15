import os
import time
import logging
from invoice_generator.utils import get_recent_json_files
from invoice_generator.survey_app import run_survey
from invoice_generator.json_to_doc_pdf import generate_invoice

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Runs the invoice generation workflow."""
    logging.info("Starting survey application...")
    run_survey()

    # Wait for files to write
    time.sleep(2)  # Short delay to ensure the file is written

    # Define directory dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
    json_directory = os.path.join(script_dir, "invoice_generator", "invoices")

    logging.info(str(json_directory))

    # Get JSON files from the last 3 hours
    recent_json_files = get_recent_json_files(json_directory, hours=3)

    if recent_json_files:
        logging.info(f"Found {len(recent_json_files)} JSON files created in the last 3 hours:")
        for json_file in recent_json_files:
            logging.info(f"Processing file: {json_file}")
            try:
                generate_invoice(json_file)
                logging.info(f"Invoice processing complete for {json_file}")
            except Exception as e:
                logging.error(f"Error processing {json_file}: {e}")
    else:
        logging.warning("No JSON files created in the last 3 hours.")

if __name__ == "__main__":
    main()
