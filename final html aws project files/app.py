"""
PlantGuard - AI Plant Disease Detection Web Application
Flask Backend Server
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
from PIL import Image
import io

# Import our modules
from model import get_classifier, get_leaf_validator
from disease_data import DISEASE_DATABASE, get_all_classes, get_disease_info, get_healthy_classes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plantguard-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Create uploads directory if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

@app.route('/favicon.ico')
def favicon():
    """Serve favicon - returns a simple green leaf icon"""
    # Simple 1x1 green pixel PNG (base64 encoded)
    import base64
    green_pixel = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
    return Response(green_pixel, mimetype='image/png')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('index.html', section='about')

@app.route('/diseases')
def diseases():
    """Disease database page"""
    return render_template('index.html', section='diseases')

@app.route('/detect')
def detect():
    """Detect page"""
    return render_template('index.html', section='detect')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image prediction request"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'})
        
        # Save the file
        filename = save_uploaded_file(file)
        if not filename:
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload PNG, JPG, or JPEG'})
        
        # Get full path for prediction
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # STEP 1: Validate if the image is a leaf using leaf_vs_nonleaf_model
        leaf_validator = get_leaf_validator()
        is_leaf, leaf_confidence = leaf_validator.is_leaf(filepath)
        
        if not is_leaf:
            # Remove the uploaded file since it's not a leaf
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': 'Please upload a leaf image properly to get accurate results. The uploaded image does not appear to be a plant leaf.',
                'is_leaf': False,
                'leaf_confidence': float(leaf_confidence) * 100
            })
        
        # STEP 2: If it's a leaf, proceed with disease detection
        # Get classifier and make prediction
        classifier = get_classifier()
        predictions = classifier.predict(filepath)
        
        # Get disease information for the top prediction
        top_prediction = predictions[0]
        disease_info = get_disease_info(top_prediction['class'])
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'disease_info': disease_info,
            'image_url': f'/uploads/{filename}',
            'is_leaf': True,
            'leaf_confidence': float(leaf_confidence) * 100
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/diseases', methods=['GET'])
def get_all_diseases():
    """Get all disease information"""
    diseases = []
    for class_name, info in DISEASE_DATABASE.items():
        diseases.append({
            'class': class_name,
            'name': info['name'],
            'plant': info['plant'],
            'severity': info['severity'],
            'symptoms': info['symptoms'][:200] + '...' if len(info['symptoms']) > 200 else info['symptoms']
        })
    return jsonify({'success': True, 'diseases': diseases})

@app.route('/api/disease/<path:disease_class>', methods=['GET'])
def get_disease(disease_class):
    """Get detailed information for a specific disease"""
    # Replace underscores with spaces for URL encoding
    disease_class = disease_class.replace('__', '___')
    disease_info = get_disease_info(disease_class)
    
    if disease_info:
        return jsonify({'success': True, 'disease': disease_info})
    return jsonify({'success': False, 'error': 'Disease not found'})

@app.route('/api/plants', methods=['GET'])
def get_plants():
    """Get list of all plants in the database"""
    plants = set()
    for class_name in DISEASE_DATABASE.keys():
        plant = class_name.split('___')[0]
        plants.add(plant)
    return jsonify({'success': True, 'plants': sorted(list(plants))})

@app.route('/api/search', methods=['GET'])
def search_diseases():
    """Search diseases by name or plant"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'success': True, 'results': []})
    
    results = []
    for class_name, info in DISEASE_DATABASE.items():
        if query in class_name.lower() or query in info['name'].lower() or query in info['plant'].lower():
            results.append({
                'class': class_name,
                'name': info['name'],
                'plant': info['plant'],
                'severity': info['severity']
            })
    
    return jsonify({'success': True, 'results': results})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Page not found'})

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'})

if __name__ == '__main__':
    print("=" * 60)
    print("🌿 PlantGuard - AI Plant Disease Detection System")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
