import os
import random
from flask import Flask, request, jsonify, render_template
from PIL import Image
import json
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from templates import select_template  # Import the templates module
from dotenv import load_dotenv
import io
import base64

# Load environment variables
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Get the API key from the .env file
api_key = os.getenv("GOOGLE_PALM_API_KEY")

# Authenticate with Google PaLM API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Route to serve the index page
@app.route('/')
def index():
    return render_template('index.html')

# Main route to execute everything and generate post content and image
@app.route('/execute_all', methods=['POST'])
def execute_all():
    data = request.get_json()
    insta_handle = data.get('insta_handle')
    business_website = data.get('business_website')
    context = data.get('context')

    if not insta_handle or not business_website:
        return jsonify({"error": "Instagram handle and business website are required!"}), 400

    try:
        # Scrape website content (keep in memory)
        scraped_content = scrape_website_content(business_website)
        print(f"Website content scraped successfully for {business_website}")
    except Exception as e:
        return jsonify({"error": "Failed to scrape the website.", "details": str(e)}), 500

    try:
        # Generate post idea (keep in memory)
        post_idea = generate_instagram_post(insta_handle, scraped_content, context)
        print(f"Post idea generated successfully for {insta_handle}")

        # Generate the image using a random template (in memory)
        img_io = generate_image(insta_handle, post_idea)
        print(f"Image generated successfully for {insta_handle}")
    except Exception as e:
        return jsonify({"error": "Failed to generate post idea or image.", "details": str(e)}), 500

    # Extract caption and hashtags
    caption = post_idea.get("caption", "Default Caption")
    hashtags = post_idea.get("hash", "#default")

    # Encode image to base64
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    return jsonify({
        "generate_post_idea": f"{caption} {hashtags}",
        "image_base64": img_base64
    })

# Scrape website content
def scrape_website_content(url):
    """Scrape all text content from the provided website."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to access website. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = ''

    for paragraph in soup.find_all('p'):
        text_content += paragraph.get_text() + '\n'

    return text_content

# Generate Instagram post idea
def generate_instagram_post(insta_handle, content, context):
    prompt = f"""
    Create a detailed Instagram post idea for the Instagram handle @{insta_handle} on theme {context} based on this website content:
    {content[:500]}.

    Don't use any emojis. Make sure not to use any emoji.
    The post should include a JSON file, with the following structure:
    - headline: content
    - caption: content
    - hash: content
    1. Ad Headlines 40 characters max.
    2. A catchy caption.
    3. Relevant hashtags (3-5 hashtags).

    Just provide me the content of the json file as it is.
    """

    response = model.generate_content(prompt)

    # Ensure the correct parsing of the API response (adjust if the structure is different)
    json_output = response.text.strip()

    # Clean the output (optional, depending on API response)
    json_output = json_output.replace("```json", "").replace("```", "").strip()

    try:
        post_idea = json.loads(json_output)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to decode JSON: {e}")

    return post_idea

# Generate the Instagram post image based on the post idea (in memory)
def generate_image(insta_handle, post_idea):
    # Extract the headline
    headline = post_idea.get("headline", "Default Headline")

    # Select a random image from the images folder
    image_number = random.randint(1, 73)
    image_filename = f"{image_number}.jpg"

    # Use the correct path to the images folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_folder = os.path.join(current_dir, 'images')
    image_path = os.path.join(image_folder, image_filename)
    
    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Image {image_filename} not found in the images folder!")
        raise Exception(f"Image {image_filename} not found in the images folder!")
    else:
        print(f"Using image: {image_path}")

    # Open and process the image
    image = Image.open(image_path)
    
    # Use a random template to modify the image
    image = select_template(image, headline, insta_handle)

    # Save the image to a BytesIO object (in memory)
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

if __name__ == '__main__':
    app.run(debug=False)
