from transformers import AutoModelForImageClassification, AutoImageProcessor
import logging

logging.basicConfig(level=logging.INFO)

def download():
    model_id = "ozair23/mobilenet_v2_1.0_224-finetuned-plantdisease"
    logging.info(f"Downloading model {model_id} to cache...")
    AutoModelForImageClassification.from_pretrained(model_id)
    AutoImageProcessor.from_pretrained(model_id)
    logging.info("Download complete.")

if __name__ == "__main__":
    download()
