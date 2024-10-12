# tasks.py
import openai
from PIL import Image
from io import BytesIO
import uuid
import os
import logging
from huggingface_hub import InferenceApi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API keys from environment variables
openai.api_key = os.environ.get('OPENAI_API_KEY')
hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')

def generate_image(prompt):
    if not hf_token:
        raise Exception("HuggingFace API token is not set.")
    
    try:
        # Set up the Inference API
        inference = InferenceApi(repo_id="stabilityai/stable-diffusion-2-1", token=hf_token)

        # Generate the image
        response = inference(inputs=prompt, params={"num_inference_steps": 50})

        # Check for errors
        if isinstance(response, dict) and 'error' in response:
            raise Exception(f"Error generating image: {response['error']}")

        # If response is a PIL Image, return it directly
        if isinstance(response, Image.Image):
            return response

        # If response is bytes, open it as image
        try:
            image = Image.open(BytesIO(response))
            return image
        except Exception as e:
            logger.error(f"Error opening image from bytes: {e}")
            raise
    except Exception as e:
        logger.error(f"Exception during image generation: {e}")
        raise

def generate_story_and_image(child_name, age, themes, additional_details):
    # Ensure child_name is safe
    child_name = child_name.strip()
    age = age.strip()
    themes = themes.strip()
    additional_details = additional_details.strip() if additional_details else ""

    try:
        # Generate the story using OpenAI API
        story_prompt = f"Write a short children's story for a child named {child_name}, who is {age} years old. The story should include themes of {themes}. {additional_details}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative and child-friendly storyteller."},
                {"role": "user", "content": story_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        story = response['choices'][0]['message']['content']
        logger.info("Story generation successful.")
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        story = "An error occurred while generating the story."

    try:
        # Generate the image
        image_prompt = f"An illustration for a children's story about {themes}"
        image = generate_image(image_prompt)
        unique_id = str(uuid.uuid4())
        image_filename = f"{unique_id}.png"
        
        # Get absolute path to static/images/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, 'static', 'images')
        os.makedirs(images_dir, exist_ok=True)
        image_path = os.path.join(images_dir, image_filename)
        image.save(image_path)
        logger.info(f"Image saved as {image_filename}.")
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        image_filename = 'placeholder.png'  # Ensure you have a placeholder image in static/images/
    
    return {'story': story, 'image_filename': image_filename}
