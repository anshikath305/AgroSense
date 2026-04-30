from transformers import AutoModelForImageClassification, AutoImageProcessor
import logging

logging.basicConfig(level=logging.INFO)

def download():
    model_id = "Abhiram4/PlantDiseaseDetectorVit2"
    logging.info(f"Downloading model {model_id} to cache...")
    AutoModelForImageClassification.from_pretrained(model_id)
    AutoImageProcessor.from_pretrained(model_id)
    logging.info("Download complete.")

if __name__ == "__main__":
    download()
