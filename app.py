from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid
from datetime import datetime
import random
import requests
from urllib.parse import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('dog_voting.db')
    cursor = conn.cursor()
    
    # Create dogs table (now includes cats too!)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_cat BOOLEAN DEFAULT FALSE,
            cat_votes INTEGER DEFAULT 0
        )
    ''')
    
    # Create votes table to track individual votes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER,
            vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dog_id) REFERENCES dogs (id)
        )
    ''')
    
    # Create cat votes table to track when people vote for cats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cat_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER,
            vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dog_id) REFERENCES dogs (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_dogs():
    """Get all dogs (and cats!) shuffled for swiping"""
    conn = sqlite3.connect('dog_voting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, original_name, votes, upload_date, is_cat, cat_votes FROM dogs')
    dogs = cursor.fetchall()
    conn.close()
    
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
    conn = sqlite3.connect('dog_voting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, original_name, votes, upload_date, is_cat, cat_votes FROM dogs')
    dogs = cursor.fetchall()
    conn.close()
    
    # Shuffle the list for random order
    random.shuffle(dogs)
    print(f"🎲 Ready to serve {len(dogs)} pictures for voting!")
    return dogs

def add_dog(filename, original_name, is_cat=False):
    """Add a new dog (or cat) to the database"""
    conn = sqlite3.connect('dog_voting.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO dogs (filename, original_name, is_cat) VALUES (?, ?, ?)', 
                   (filename, original_name, is_cat))
    conn.commit()
    conn.close()

def inject_random_cat():
    """Inject a random cat photo from an online service"""
    try:
        # Use multiple cat APIs for better reliability
        cat_apis = [
            # Direct image URLs from cataas.com
            {
                'type': 'direct',
                'urls': [
                    "https://cataas.com/cat/cute",
                    "https://cataas.com/cat/orange", 
                    "https://cataas.com/cat/fluffy",
                    "https://cataas.com/cat/kitten",
                    "https://cataas.com/cat/sleepy",
                    "https://cataas.com/cat/small",
                    "https://cataas.com/cat/bengal"
                ]
            },
            # JSON API from thecatapi.com
            {
                'type': 'json',
                'url': "https://api.thecatapi.com/v1/images/search",
                'key': 'url'
            }
        ]
        
        # Try each API approach
        for api in cat_apis:
            try:
                if api['type'] == 'direct':
                    # Direct image URL approach
                    cat_url = random.choice(api['urls'])
                    response = requests.get(cat_url, timeout=15)
                    
                    if response.status_code == 200:
                        # Generate unique filename for cat
                        cat_filename = f"cat_{uuid.uuid4().hex}.jpg"
                        cat_path = os.path.join(app.config['UPLOAD_FOLDER'], cat_filename)
                        
                        # Create upload directory if it doesn't exist
                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        
                        # Save cat image
                        with open(cat_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Add to database as a cat
                        cat_names = [
                            "Suspicious Cat 🤔", 
                            "Sneaky Kitty 😼", 
                            "Plot Twist Cat 🐱", 
                            "Not a Dog! 😸",
                            "Attention Test Cat 🙀",
                            "Gotcha Cat 😹",
                            "Meow Imposter 🐾",
                            "Feline Infiltrator 🕵️",
                            "Whiskers Wannabe 😽",
                            "Test Subject Mittens 🧪"
                        ]
                        add_dog(cat_filename, random.choice(cat_names), is_cat=True)
                        print(f"✅ Injected random cat: {cat_filename}")
                        return True
                        
                elif api['type'] == 'json':
                    # JSON API approach
                    response = requests.get(api['url'], timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0 and api['key'] in data[0]:
                            image_url = data[0][api['key']]
                            
                            # Download the actual image
                            img_response = requests.get(image_url, timeout=15)
                            if img_response.status_code == 200:
                                # Determine file extension
                                file_ext = 'jpg'
                                if '.' in image_url:
                                    file_ext = image_url.split('.')[-1].lower().split('?')[0]
                                    if file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                        file_ext = 'jpg'
                                
                                # Generate unique filename for cat
                                cat_filename = f"cat_{uuid.uuid4().hex}.{file_ext}"
                                cat_path = os.path.join(app.config['UPLOAD_FOLDER'], cat_filename)
                                
                                # Create upload directory if it doesn't exist
                                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                                
                                # Save cat image
                                with open(cat_path, 'wb') as f:
                                    f.write(img_response.content)
                                
                                # Add to database as a cat
                                cat_names = [
                                    "Suspicious Cat 🤔", 
                                    "Sneaky Kitty 😼", 
                                    "Plot Twist Cat 🐱", 
                                    "Not a Dog! 😸",
                                    "Attention Test Cat 🙀",
                                    "Gotcha Cat 😹",
                                    "Meow Imposter 🐾",
                                    "Feline Infiltrator 🕵️",
                                    "Whiskers Wannabe 😽",
                                    "Test Subject Mittens 🧪"
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

def inject_random_dog():
    """Inject a random dog photo from online dog APIs"""
    try:
        # Use various dog APIs for random dog photos
        dog_apis = [
            "https://dog.ceo/api/breeds/image/random",  # Returns JSON with message field
            "https://random.dog/woof.json",  # Returns JSON with url field
            "https://api.thedogapi.com/v1/images/search",  # TheDogAPI format
        ]
        
        # Try different approaches for different APIs
        for api_url in dog_apis:
            try:
                response = requests.get(api_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract image URL based on API format
                    if 'message' in data:  # dog.ceo format
                        image_url = data['message']
                    elif 'url' in data:  # random.dog format
                        image_url = data['url']
                    elif isinstance(data, list) and len(data) > 0 and 'url' in data[0]:  # thedogapi format
                        image_url = data[0]['url']
                    else:
                        continue
                    
                    # Skip if URL contains video formats
                    if any(ext in image_url.lower() for ext in ['.mp4', '.webm', '.mov', '.avi']):
                        continue
                    
                    # Download the actual image
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Determine file extension from URL or default to jpg
                        file_ext = 'jpg'
                        if '.' in image_url:
                            file_ext = image_url.split('.')[-1].lower().split('?')[0]  # Remove query params
                            if file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                file_ext = 'jpg'
                        
                        # Generate unique filename for dog
                        dog_filename = f"generated_dog_{uuid.uuid4().hex}.{file_ext}"
                        dog_path = os.path.join(app.config['UPLOAD_FOLDER'], dog_filename)
                        
                        # Create upload directory if it doesn't exist
                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        
                        # Save dog image
                        with open(dog_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Add to database as a generated dog
                        dog_names = [
                            "Internet Doggo 🌐",
                            "Random Good Boy 🦴", 
                            "Mystery Pup 🔍",
                            "Generated Goodness 🤖",
                            "Algorithm's Choice 💫",
                            "Digital Doggy 📱",
                            "Code Canine 💻",
                            "Pixel Pup 🎨",
                            "Random Rescue 🎲",
                            "Virtual Buddy 🎮",
                            "API Fetched Friend 🚀",
                            "Cloud Canine ☁️",
                            "Randomly Selected Rex 🎯"
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

def vote_for_dog(dog_id):
    """Add a vote for a specific dog (or track cat votes separately!)"""
    conn = sqlite3.connect('dog_voting.db')
    cursor = conn.cursor()
    
    # Check if this is a cat
    cursor.execute('SELECT is_cat FROM dogs WHERE id = ?', (dog_id,))
    result = cursor.fetchone()
    
    if result and result[0]:  # This is a cat!
        # Track cat votes separately
        cursor.execute('INSERT INTO cat_votes (dog_id) VALUES (?)', (dog_id,))
        cursor.execute('UPDATE dogs SET cat_votes = cat_votes + 1 WHERE id = ?', (dog_id,))
        conn.commit()
        conn.close()
        return "cat"
    else:  # This is a dog
        # Add vote to votes table
        cursor.execute('INSERT INTO votes (dog_id) VALUES (?)', (dog_id,))
        # Update vote count in dogs table
        cursor.execute('UPDATE dogs SET votes = votes + 1 WHERE id = ?', (dog_id,))
        conn.commit()
        conn.close()
        return "dog"

@app.route('/')
def index():
    """Main page showing all dogs"""
    dogs = get_all_dogs()
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
            
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Save file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Add to database
            add_dog(unique_filename, file.filename)
            
            flash('Dog picture uploaded successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP files.', 'error')
    
    return render_template('upload.html')

@app.route('/vote/<int:dog_id>')
def vote(dog_id):
    """Vote for a specific dog"""
    try:
        vote_for_dog(dog_id)
        flash('Thanks for voting!', 'success')
    except Exception as e:
        flash('Error recording vote. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/vote/<int:dog_id>', methods=['POST'])
def api_vote(dog_id):
    """API endpoint for voting (for AJAX requests)"""
    try:
        vote_type = vote_for_dog(dog_id)
        
        # Get updated vote count
        conn = sqlite3.connect('dog_voting.db')
        cursor = conn.cursor()
        if vote_type == "cat":
            cursor.execute('SELECT cat_votes, original_name FROM dogs WHERE id = ?', (dog_id,))
            result = cursor.fetchone()
            votes = result[0]
            cat_name = result[1]
            conn.close()
            return jsonify({
                'success': True, 
                'votes': votes, 
                'is_cat': True, 
                'cat_name': cat_name,
                'message': "😹 You just voted for a cat! Were you paying attention?"
            })
        else:
            cursor.execute('SELECT votes FROM dogs WHERE id = ?', (dog_id,))
            votes = cursor.fetchone()[0]
            conn.close()
            return jsonify({'success': True, 'votes': votes, 'is_cat': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 