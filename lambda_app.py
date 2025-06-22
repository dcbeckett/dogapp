import json
import boto3
import uuid
import random
import requests
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
import serverless_wsgi
from botocore.exceptions import ClientError

# AWS Configuration
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your-dog-voting-bucket')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'dog-voting-table')
AWS_REGION = os.environ.get('REGION', 'us-east-1')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['S3_BUCKET_NAME'] = BUCKET_NAME

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_all_dogs():
    """Get all dogs (and cats!) shuffled for swiping"""
    try:
        response = table.scan()
        dogs = response['Items']
        
        # Ensure we have at least 100 pictures total
        current_count = len(dogs)
        min_required = 100
        
        if current_count < min_required:
            # Calculate how many we need to add
            needed = min_required - current_count
            print(f"📊 Current photos: {current_count}, need {needed} more to reach minimum {min_required}")
            
            # Add the required number of pictures
            # Mix of mostly dogs (80%) and some cats (20%) for attention testing
            cats_to_add = max(1, needed // 5)  # At least 1 cat, or ~20% of needed
            dogs_to_add = needed - cats_to_add
            
            print(f"🐕 Adding {dogs_to_add} dogs and 🐱 {cats_to_add} cats")
            
            # Add the dogs first
            for i in range(dogs_to_add):
                success = inject_random_dog()
                if not success:
                    print(f"⚠️ Failed to add dog {i+1}/{dogs_to_add}")
            
            # Add the cats
            for i in range(cats_to_add):
                success = inject_random_cat()
                if not success:
                    print(f"⚠️ Failed to add cat {i+1}/{cats_to_add}")
        
        elif random.random() < 0.3:  # 30% chance to add bonus content when we have enough
            # Randomly choose what to inject for variety
            roll = random.random()
            if roll < 0.2:  # 20% chance for cat (attention test)
                inject_random_cat()
            else:  # 80% chance for dog (more content)
                inject_random_dog()
        
        # Fetch again to include any new animals
        response = table.scan()
        dogs = response['Items']
        
        # Convert DynamoDB items to SQLite tuple format for template compatibility
        # Expected format: (id, filename, original_name, votes, upload_date, is_cat, cat_votes)
        dogs_tuples = []
        for dog in dogs:
            dog_tuple = (
                dog.get('id', ''),
                dog.get('filename', ''),
                dog.get('original_name', ''),
                int(dog.get('votes', 0)),
                dog.get('upload_date', ''),
                bool(dog.get('is_cat', False)),
                int(dog.get('cat_votes', 0))
            )
            dogs_tuples.append(dog_tuple)
        
        # Shuffle the list for random order
        random.shuffle(dogs_tuples)
        print(f"🎲 Ready to serve {len(dogs_tuples)} pictures for voting!")
        return dogs_tuples
        
    except Exception as e:
        print(f"Error getting dogs: {e}")
        return []

def add_dog(filename, original_name, is_cat=False):
    """Add a new dog (or cat) to DynamoDB"""
    try:
        item = {
            'id': str(uuid.uuid4()),
            'filename': filename,
            'original_name': original_name,
            'votes': 0,
            'upload_date': datetime.now().isoformat(),
            'is_cat': is_cat,
            'cat_votes': 0
        }
        table.put_item(Item=item)
        return item['id']
    except Exception as e:
        print(f"Error adding dog: {e}")
        return None

def inject_random_dog():
    """Inject a random dog photo from online dog APIs and upload to S3"""
    try:
        # Use various dog APIs for random dog photos
        dog_apis = [
            "https://dog.ceo/api/breeds/image/random",
            "https://random.dog/woof.json",
            "https://api.thedogapi.com/v1/images/search",
        ]
        
        for api_url in dog_apis:
            try:
                response = requests.get(api_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract image URL based on API format
                    if 'message' in data:
                        image_url = data['message']
                    elif 'url' in data:
                        image_url = data['url']
                    elif isinstance(data, list) and len(data) > 0 and 'url' in data[0]:
                        image_url = data[0]['url']
                    else:
                        continue
                    
                    # Skip video formats
                    if any(ext in image_url.lower() for ext in ['.mp4', '.webm', '.mov', '.avi']):
                        continue
                    
                    # Download the image
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Generate filename
                        file_ext = 'jpg'
                        if '.' in image_url:
                            file_ext = image_url.split('.')[-1].lower().split('?')[0]
                            if file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                file_ext = 'jpg'
                        
                        dog_filename = f"generated_dog_{uuid.uuid4().hex}.{file_ext}"
                        
                        # Upload to S3
                        s3_client.put_object(
                            Bucket=BUCKET_NAME,
                            Key=f"uploads/{dog_filename}",
                            Body=img_response.content,
                            ContentType=f'image/{file_ext}'
                        )
                        
                        # Add to database
                        dog_names = [
                            "Internet Doggo 🌐", "Random Good Boy 🦴", "Mystery Pup 🔍",
                            "Generated Goodness 🤖", "Algorithm's Choice 💫", "Digital Doggy 📱",
                            "Code Canine 💻", "Pixel Pup 🎨", "Random Rescue 🎲", "Virtual Buddy 🎮",
                            "API Fetched Friend 🚀", "Cloud Canine ☁️", "Randomly Selected Rex 🎯"
                        ]
                        add_dog(dog_filename, random.choice(dog_names), is_cat=False)
                        print(f"✅ Injected random dog: {dog_filename}")
                        return True
            except Exception as api_error:
                print(f"Failed with API {api_url}: {api_error}")
                continue
                
        return False
    except Exception as e:
        print(f"Failed to inject dog: {e}")
        return False

def inject_random_cat():
    """Inject a random cat photo from online services and upload to S3"""
    try:
        # Cat APIs
        cat_apis = [
            {
                'type': 'direct',
                'urls': [
                    "https://cataas.com/cat/cute", "https://cataas.com/cat/orange", 
                    "https://cataas.com/cat/fluffy", "https://cataas.com/cat/kitten",
                    "https://cataas.com/cat/sleepy", "https://cataas.com/cat/small"
                ]
            },
            {
                'type': 'json',
                'url': "https://api.thecatapi.com/v1/images/search",
                'key': 'url'
            }
        ]
        
        for api in cat_apis:
            try:
                if api['type'] == 'direct':
                    cat_url = random.choice(api['urls'])
                    response = requests.get(cat_url, timeout=15)
                    
                    if response.status_code == 200:
                        cat_filename = f"cat_{uuid.uuid4().hex}.jpg"
                        
                        # Upload to S3
                        s3_client.put_object(
                            Bucket=BUCKET_NAME,
                            Key=f"uploads/{cat_filename}",
                            Body=response.content,
                            ContentType='image/jpeg'
                        )
                        
                        # Add to database
                        cat_names = [
                            "Suspicious Cat 🤔", "Sneaky Kitty 😼", "Plot Twist Cat 🐱", 
                            "Not a Dog! 😸", "Attention Test Cat 🙀", "Gotcha Cat 😹",
                            "Meow Imposter 🐾", "Feline Infiltrator 🕵️", "Whiskers Wannabe 😽"
                        ]
                        add_dog(cat_filename, random.choice(cat_names), is_cat=True)
                        print(f"✅ Injected random cat: {cat_filename}")
                        return True
                        
                elif api['type'] == 'json':
                    response = requests.get(api['url'], timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0 and api['key'] in data[0]:
                            image_url = data[0][api['key']]
                            
                            img_response = requests.get(image_url, timeout=15)
                            if img_response.status_code == 200:
                                file_ext = 'jpg'
                                if '.' in image_url:
                                    file_ext = image_url.split('.')[-1].lower().split('?')[0]
                                    if file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                        file_ext = 'jpg'
                                
                                cat_filename = f"cat_{uuid.uuid4().hex}.{file_ext}"
                                
                                # Upload to S3
                                s3_client.put_object(
                                    Bucket=BUCKET_NAME,
                                    Key=f"uploads/{cat_filename}",
                                    Body=img_response.content,
                                    ContentType=f'image/{file_ext}'
                                )
                                
                                # Add to database
                                cat_names = [
                                    "Suspicious Cat 🤔", "Sneaky Kitty 😼", "Plot Twist Cat 🐱", 
                                    "Not a Dog! 😸", "Attention Test Cat 🙀", "Gotcha Cat 😹",
                                    "Meow Imposter 🐾", "Feline Infiltrator 🕵️", "Whiskers Wannabe 😽"
                                ]
                                add_dog(cat_filename, random.choice(cat_names), is_cat=True)
                                print(f"✅ Injected random cat: {cat_filename}")
                                return True
                                
            except Exception as api_error:
                print(f"Failed with cat API {api}: {api_error}")
                continue
                
        return False
    except Exception as e:
        print(f"Failed to inject cat: {e}")
        return False

def vote_for_dog(dog_id):
    """Add a vote for a specific dog"""
    try:
        # Get the dog item
        response = table.get_item(Key={'id': dog_id})
        if 'Item' not in response:
            return None
            
        item = response['Item']
        is_cat = item.get('is_cat', False)
        
        if is_cat:
            # Update cat votes
            table.update_item(
                Key={'id': dog_id},
                UpdateExpression='SET cat_votes = cat_votes + :val',
                ExpressionAttributeValues={':val': 1}
            )
            return "cat"
        else:
            # Update dog votes
            table.update_item(
                Key={'id': dog_id},
                UpdateExpression='SET votes = votes + :val',
                ExpressionAttributeValues={':val': 1}
            )
            return "dog"
            
    except Exception as e:
        print(f"Error voting: {e}")
        return None

@app.route('/')
def index():
    """Main page showing all dogs"""
    dogs = get_all_dogs()
    # Generate S3 URLs for images
    for dog in dogs:
        dog['image_url'] = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/uploads/{dog['filename']}"
    return render_template('index.html', dogs=dogs)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Upload a new dog picture"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Upload to S3
            try:
                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=f"uploads/{unique_filename}",
                    Body=file.read(),
                    ContentType=f'image/{file_extension}'
                )
                
                # Add to database
                add_dog(unique_filename, file.filename)
                
                flash('Dog picture uploaded successfully!', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                print(f"Upload error: {e}")
                flash('Error uploading file. Please try again.', 'error')
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP files.', 'error')
    
    return render_template('upload.html')

@app.route('/api/vote/<dog_id>', methods=['POST'])
def api_vote(dog_id):
    """API endpoint for voting (for AJAX requests)"""
    try:
        vote_type = vote_for_dog(dog_id)
        
        if vote_type == "cat":
            # Get updated cat info
            response = table.get_item(Key={'id': dog_id})
            item = response['Item']
            return jsonify({
                'success': True, 
                'votes': item['cat_votes'], 
                'is_cat': True, 
                'cat_name': item['original_name'],
                'message': "😹 You just voted for a cat! Were you paying attention?"
            })
        elif vote_type == "dog":
            # Get updated dog info
            response = table.get_item(Key={'id': dog_id})
            item = response['Item']
            return jsonify({'success': True, 'votes': item['votes'], 'is_cat': False})
        else:
            return jsonify({'success': False, 'error': 'Dog not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_file'))

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

# Lambda handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context) 