import json
from flask import Flask, request, jsonify, render_template, send_file, url_for
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import os
import random

# Initialize the Flask app
app = Flask(__name__)

# Ensure the static/images directory exists for generated images
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Authenticate with Google PaLM API
genai.configure(api_key="AIzaSyD68l2JzBQW01WroV8LaOWqpEltqLrr7R4")  # Replace this with your actual API key
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
    context = data.get('context')  # Context is fetched here

    if not insta_handle or not business_website:
        return jsonify({"error": "Instagram handle and business website are required!"}), 400

    try:
        scraped_content = scrape_website_content(business_website)
        with open('scraped.txt', 'w') as file:
            file.write(scraped_content)
    except Exception as e:
        return jsonify({"error": "Failed to scrape the website.", "details": str(e)}), 500

    try:
        # Pass context to generate_instagram_post
        post_idea = generate_instagram_post(insta_handle, scraped_content, context)  # context is passed here

        # Store the post idea in a JSON file
        with open('idea.json', 'w') as json_file:
            json.dump(post_idea, json_file, indent=4)  # Save the post idea in structured JSON format

        # Generate the image based on the contents of the idea.json file
        generated_image_path = generate_image(insta_handle)
        print(f"Image generated at: {generated_image_path}")  # Debugging statement

    except Exception as e:
        return jsonify({"error": "Failed to generate post idea or image.", "details": str(e)}), 500

    # Use url_for to return the correct path to the image
    image_url = url_for('static', filename=f'images/{os.path.basename(generated_image_path)}')

    with open('idea.json', 'r') as json_file:
        post_idea = json.load(json_file)

    # Extract the headline, caption, and hashtags from the JSON file
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

    # Extract the headline, caption, and hashtags from the JSON file
    headline = post_idea.get("headline", "Default Headline")
    caption = post_idea.get("caption", "Default Caption")
    hashtags = post_idea.get("hash", "#default")

    # Generate a random number to select an image from 1.jpg to 73.jpg
    image_number = random.randint(1, 73)
    image_filename = f"{image_number}.jpg"

    # Path to the source image folder
    image_folder = 'images'  # This is the folder where your original images are stored

    # Construct the full image path
    image_path = os.path.join(image_folder, image_filename)
    print(f"Using image: {image_path}")  # Debugging statement

    # Check if the selected image exists, if not raise an exception
    if not os.path.exists(image_path):
        raise Exception(f"Image {image_filename} not found in the images folder!")

    # Load the randomly selected image
    image = Image.open(image_path)

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define fonts (Use the downloaded Roboto fonts from Google Fonts)
    try:
        font_large = ImageFont.truetype("Roboto/Roboto-Bold.ttf", 50)  # For tagline (headline)
        font_small = ImageFont.truetype("Roboto/Roboto-Regular.ttf", 30)  # For contact info and website
    except IOError:
        print("Font file not found, loading default fonts.")
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Create a black rectangle at the top for the tagline (headline)
    rectangle_height_top = 150  # Adjust the height of the black box as needed
    draw.rectangle([0, 0, image.width, rectangle_height_top], fill="black")

    # Adding the headline on top of the black box
    draw.text((50, 30), headline, font=font_large, fill="white")  # Adjust the position (50, 30) as needed

    # Create a blue rectangle bar at the bottom
    rectangle_height_bottom = 80
    draw.rectangle([0, image.height - rectangle_height_bottom, image.width, image.height], fill="#1a73e8")

    # Adding contact info and website
    contact_info = "+91 9893034016"  # Phone number
    website = f"@{insta_handle}"  # Instagram handle

    # Positioning for the website on the left bottom
    left_margin = 50
    draw.text((left_margin, image.height - 60), website, font=font_small, fill="white")

    # Positioning for the phone number on the right bottom
    bbox = draw.textbbox((0, 0), contact_info, font=font_small)
    text_width = bbox[2] - bbox[0]  # Width of the text
    right_margin = image.width - text_width - 50  # Adjust to place the text 50 pixels from the right edge
    draw.text((right_margin, image.height - 60), contact_info, font=font_small, fill="white")

    # Save the image in the static/images folder (for generated images)
    generated_image_folder = 'static/images'
    os.makedirs(generated_image_folder, exist_ok=True)
    generated_image_path = os.path.join(generated_image_folder, f'{insta_handle}_post.png')
    image.save(generated_image_path)
    print(f"Image saved at: {generated_image_path}")  # Debugging statement

    return generated_image_path

if __name__ == '__main__':
    app.run(debug=True)

