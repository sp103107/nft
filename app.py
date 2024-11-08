import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr

# Load environment variables from .env
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Hugging Face API URL for Stable Diffusion with diffusers
HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Load prompts from prompts/prompts.json
def load_prompts(filename="prompts/prompts.json"):
    with open(filename, "r") as file:
        return json.load(file)

# Function to call Hugging Face API and generate an image with retry
def generate_image(prompt_text, output_path, retries=3, delay=5):
    for attempt in range(retries):
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt_text})
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Image saved to {output_path}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    print(f"Failed to generate image for prompt after {retries} attempts.")
    return False

# Batch generation function for handling up to 100 images
def generate_batch(batch_id):
    prompts = load_prompts()
    batch_metadata = []
    image_dir = Path(f"images/batch_{batch_id}")
    image_dir.mkdir(parents=True, exist_ok=True)

    for i, theme in enumerate(prompts.keys(), 1):
        if i > 100:
            break  # Stop after generating 100 images
        prompt_data = prompts[theme]
        print(f"Debug: Processing theme {theme} for batch_id {batch_id}")

        required_keys = ['style', 'features', 'background']
        missing_keys = [key for key in required_keys if key not in prompt_data]
        
        if missing_keys:
            print(f"Error: Missing keys {missing_keys} in prompt_data for batch_id {batch_id}")
            continue

        prompt_text = f"{prompt_data['style']} with {', '.join(prompt_data['features'])}, in {prompt_data['background']}."
        image_path = image_dir / f"{theme}_avatar_{batch_id}_{i}.jpeg"
        
        # Generate image and save if successful
        if generate_image(prompt_text, image_path):
            metadata = {
                "id": f"{theme}_avatar_{batch_id}_{i}",
                "theme": theme,
                "prompt_text": prompt_text,
                "image_path": str(image_path),
            }
            batch_metadata.append(metadata)

    # Save metadata to JSON file
    metadata_file = Path(f"metadata/batch_{batch_id}.json")
    metadata_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with open(metadata_file, "w") as f:
        json.dump(batch_metadata, f, indent=4)

    print(f"Batch {batch_id} generated with {len(batch_metadata)} avatars.")
    return batch_metadata

# Gradio interface function
def gradio_generate(batch_id=1):
    metadata = generate_batch(batch_id)
    output_paths = [meta["image_path"] for meta in metadata]
    return output_paths

# Define Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# NFT Image Generator")
    batch_id_input = gr.Number(label="Batch ID", value=1, precision=0)
    generate_button = gr.Button("Generate Images")
    output_gallery = gr.Gallery(label="Generated Images", show_label=False)

    generate_button.click(
        fn=gradio_generate, 
        inputs=batch_id_input, 
        outputs=output_gallery
    )

# Launch Gradio interface
if __name__ == "__main__":
    demo.launch()