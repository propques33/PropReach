import os
import random
from flask import Flask, request, jsonify, render_template, url_for
from PIL import Image
import json
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from templates import select_template  # Import the templates module
from dotenv import load_dotenv

# Initialize the Flask app
app = Flask(__name__)

# Ensure the static/images directory exists for generated images
if not os.path.exists('static/images'):
    os.makedirs('static/images')

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
        scraped_content = scrape_website_content(business_website)
        with open('scraped.txt', 'w') as file:
            file.write(scraped_content)
    except Exception as e:
        return jsonify({"error": "Failed to scrape the website.", "details": str(e)}), 500

    try:
        post_idea = generate_instagram_post(insta_handle, scraped_content, context)

        # Store the post idea in a JSON file
        with open('idea.json', 'w') as json_file:
            json.dump(post_idea, json_file, indent=4)

        # Generate the image using a random template
        generated_image_path = generate_image(insta_handle)
        print(f"Image generated at: {generated_image_path}")

    except Exception as e:
        return jsonify({"error": "Failed to generate post idea or image.", "details": str(e)}), 500

    image_url = url_for('static', filename=f'images/{os.path.basename(generated_image_path)}')

    with open('idea.json', 'r') as json_file:
        post_idea = json.load(json_file)

    caption = post_idea.get("caption", "Default Caption")
    hashtags = post_idea.get("hash", "#default")

    return jsonify({
        "generate_post_idea": f"{caption} {hashtags}",
        "image_url": image_url
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
def generate_instagram_post(insta_handle, content, context):  # Add context as parameter
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

# Generate the Instagram post image based on the data in idea.json
def generate_image(insta_handle):
    # Load the post idea from idea.json file
    with open('idea.json', 'r') as json_file:
        post_idea = json.load(json_file)

    # Extract the headline
    headline = post_idea.get("headline", "Default Headline")

    # Select a random image from the images folder
    image_number = random.randint(1, 73)
    image_filename = f"{image_number}.jpg"
    image_folder = 'images'

    image_path = os.path.join(image_folder, image_filename)
    print(f"Using image: {image_path}")

    if not os.path.exists(image_path):
        raise Exception(f"Image {image_filename} not found in the images folder!")

    image = Image.open(image_path)

    # Use a random template to modify the image
    image = select_template(image, headline, insta_handle)

    generated_image_folder = 'static/images'
    os.makedirs(generated_image_folder, exist_ok=True)
    generated_image_path = os.path.join(generated_image_folder, f'{insta_handle}_post.png')
    image.save(generated_image_path)
    print(f"Image saved at: {generated_image_path}")

    return generated_image_path

if __name__ == '__main__':
    app.run(debug=True)
