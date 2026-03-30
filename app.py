from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import base64
from werkzeug.utils import secure_filename
import uuid
import shutil
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='web')
CORS(app)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(PROJECT_ROOT, 'web')
PROJECTS_DIR = os.path.join(PROJECT_ROOT, 'projects')

os.makedirs(PROJECTS_DIR, exist_ok=True)

def get_project_config(project_name):
    return {
        'name': project_name,
        'data_dir': os.path.join(PROJECTS_DIR, project_name, 'data'),
        'images_dir': os.path.join(PROJECTS_DIR, project_name, 'data', 'images'),
        'labels_dir': os.path.join(PROJECTS_DIR, project_name, 'data', 'labels'),
        'classes_file': os.path.join(PROJECTS_DIR, project_name, 'data', 'classes.json'),
        'runs_dir': os.path.join(PROJECTS_DIR, project_name, 'runs'),
        'dataset_dir': os.path.join(PROJECTS_DIR, project_name, 'dataset', 'yolo_format')
    }

def get_current_project():
    config_file = os.path.join(PROJECTS_DIR, '.current_project')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            name = f.read().strip()
            proj_path = os.path.join(PROJECTS_DIR, name)
            if os.path.exists(proj_path):
                return name
    
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
    if projects:
        set_current_project(projects[0])
        return projects[0]
    return None

def set_current_project(name):
    os.makedirs(os.path.join(PROJECTS_DIR, name, 'data'), exist_ok=True)
    config_file = os.path.join(PROJECTS_DIR, '.current_project')
    with open(config_file, 'w') as f:
        f.write(name)

current_project = get_current_project()
if current_project is None:
    current_project = 'default'
    set_current_project(current_project)
config = get_project_config(current_project)

DATA_DIR = config['data_dir']
IMAGES_DIR = config['images_dir']
LABELS_DIR = config['labels_dir']
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'dataset', 'uploads')

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

detection_model = None
detection_model_path = None
detection_device = None

def get_detection_device():
    """Check and return available device (GPU or CPU)"""
    global detection_device
    if detection_device is not None:
        return detection_device
    
    try:
        import torch
        if torch.cuda.is_available():
            try:
                cc = torch.cuda.get_device_capability(0)
                supported_ccs = [(5,0), (6,0), (6,1), (6,2), (7,0), (7,5), (8,0), (8,6), (8,7), (8,9), (9,0)]
                if cc in supported_ccs:
                    device = 'cuda'
                    print(f"[DEVICE] Using GPU: {torch.cuda.get_device_name(0)} (CC {cc[0]}.{cc[1]})")
                else:
                    device = 'cpu'
                    print(f"[DEVICE] GPU CC {cc[0]}.{cc[1]} not supported by PyTorch, using CPU")
            except Exception:
                device = 'cpu'
                print(f"[DEVICE] GPU detected but not compatible, using CPU")
        else:
            device = 'cpu'
            print(f"[DEVICE] GPU not available, using CPU")
        detection_device = device
        return device
    except Exception as e:
        print(f"[DEVICE] Error checking GPU: {e}")
        detection_device = 'cpu'
        return 'cpu'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = []
    current = get_current_project()
    for name in os.listdir(PROJECTS_DIR):
        if name.startswith('.'):
            continue
        proj_path = os.path.join(PROJECTS_DIR, name)
        if os.path.isdir(proj_path):
            images_dir = os.path.join(proj_path, 'data', 'images')
            labels_dir = os.path.join(proj_path, 'data', 'labels')
            image_count = len([f for f in os.listdir(images_dir)]) if os.path.exists(images_dir) else 0
            labeled_count = len([f for f in os.listdir(labels_dir) if f.endswith('.json')]) if os.path.exists(labels_dir) else 0
            projects.append({
                'name': name,
                'image_count': image_count,
                'labeled_count': labeled_count,
                'is_current': name == current,
                'created': datetime.fromtimestamp(os.path.getctime(proj_path)).strftime('%d/%m/%Y %H:%M')
            })
    projects.sort(key=lambda x: x['is_current'], reverse=True)
    return jsonify({'projects': projects, 'current': current})

@app.route('/api/projects', methods=['POST'])
def create_project():
    global DATA_DIR, IMAGES_DIR, LABELS_DIR, current_project, config
    
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Tên dự án không được trống'}), 400
    
    name = secure_filename(name)
    if not name:
        return jsonify({'success': False, 'message': 'Tên dự án không hợp lệ'}), 400
    
    proj_path = os.path.join(PROJECTS_DIR, name)
    if os.path.exists(proj_path):
        return jsonify({'success': False, 'message': 'Dự án đã tồn tại'}), 400
    
    os.makedirs(os.path.join(proj_path, 'data', 'images'), exist_ok=True)
    os.makedirs(os.path.join(proj_path, 'data', 'labels'), exist_ok=True)
    
    set_current_project(name)
    current_project = name
    config = get_project_config(current_project)
    DATA_DIR = config['data_dir']
    IMAGES_DIR = config['images_dir']
    LABELS_DIR = config['labels_dir']
    
    return jsonify({'success': True, 'message': f'Đã tạo dự án "{name}"', 'current': name})

@app.route('/api/projects/switch', methods=['POST'])
def switch_project():
    global DATA_DIR, IMAGES_DIR, LABELS_DIR, current_project, config
    
    data = request.json
    name = data.get('name', '')
    
    proj_path = os.path.join(PROJECTS_DIR, name)
    if not os.path.exists(proj_path):
        return jsonify({'success': False, 'message': 'Dự án không tồn tại'}), 404
    
    set_current_project(name)
    current_project = name
    config = get_project_config(current_project)
    DATA_DIR = config['data_dir']
    IMAGES_DIR = config['images_dir']
    LABELS_DIR = config['labels_dir']
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(LABELS_DIR, exist_ok=True)
    
    return jsonify({'success': True, 'message': f'Đã chuyển sang dự án "{name}"', 'current': name})

@app.route('/api/projects/<name>', methods=['DELETE'])
def delete_project(name):
    global current_project, DATA_DIR, IMAGES_DIR, LABELS_DIR, config
    
    proj_path = os.path.join(PROJECTS_DIR, name)
    if not os.path.exists(proj_path):
        return jsonify({'success': False, 'message': 'Dự án không tồn tại'}), 404
    
    shutil.rmtree(proj_path)
    
    if current_project == name:
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
        if projects:
            set_current_project(projects[0])
            current_project = projects[0]
            config = get_project_config(current_project)
            DATA_DIR = config['data_dir']
            IMAGES_DIR = config['images_dir']
            LABELS_DIR = config['labels_dir']
        else:
            current_project = None
            DATA_DIR = None
            IMAGES_DIR = None
            LABELS_DIR = None
            config_file = os.path.join(PROJECTS_DIR, '.current_project')
            if os.path.exists(config_file):
                os.remove(config_file)
    
    return jsonify({'success': True, 'message': f'Đã xóa dự án "{name}"'})

@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(WEB_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(WEB_DIR, 'js'), filename)

@app.route('/api/images', methods=['GET'])
def get_images():
    images = []
    for filename in os.listdir(IMAGES_DIR):
        if allowed_file(filename):
            label_file = os.path.join(LABELS_DIR, filename.rsplit('.', 1)[0] + '.json')
            label_data = None
            if os.path.exists(label_file):
                with open(label_file, 'r') as f:
                    label_data = json.load(f)
            images.append({
                'id': filename.rsplit('.', 1)[0],
                'filename': filename,
                'labeled': label_data is not None and len(label_data.get('annotations', [])) > 0,
                'annotations': label_data.get('annotations', []) if label_data else []
            })
    return jsonify(images)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}.{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'id': unique_id,
            'filename': filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/api/labels/<filename>', methods=['GET'])
def get_label(filename):
    label_file = os.path.join(LABELS_DIR, filename.rsplit('.', 1)[0] + '.json')
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'annotations': []})

@app.route('/api/labels/<filename>', methods=['POST'])
def save_label(filename):
    data = request.json
    label_file = os.path.join(LABELS_DIR, filename.rsplit('.', 1)[0] + '.json')
    with open(label_file, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'success': True})

@app.route('/api/dataset/export', methods=['POST'])
def export_dataset():
    """Export labeled images to YOLO format - theo dự án hiện tại"""
    project_name = get_current_project()
    if not project_name:
        return jsonify({'success': False, 'message': 'Chưa có dự án!'}), 400
    
    project_runs_dir = os.path.join(PROJECTS_DIR, project_name, 'runs')
    output_dir = os.path.join(project_runs_dir, 'dataset')
    
    os.makedirs(os.path.join(output_dir, 'images', 'train'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images', 'val'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels', 'train'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels', 'val'), exist_ok=True)
    
    # Load classes from config
    classes_config = []
    classes_file = os.path.join(DATA_DIR, 'classes.json')
    if os.path.exists(classes_file):
        with open(classes_file, 'r') as f:
            classes_config = json.load(f).get('classes', [])
    
    exported_count = 0
    val_count = 0
    train_count = 0
    
    for idx, filename in enumerate(os.listdir(IMAGES_DIR)):
        if not allowed_file(filename):
            continue
        
        label_file = os.path.join(LABELS_DIR, filename.rsplit('.', 1)[0] + '.json')
        if not os.path.exists(label_file):
            continue
            
        with open(label_file, 'r') as f:
            label_data = json.load(f)
            
        if not label_data.get('annotations'):
            continue
        
        img_path = os.path.join(IMAGES_DIR, filename)
        
        # Ensure at least 1 image goes to val if total >= 2
        if exported_count == 0:
            split = 'train'
        elif exported_count == 1 and idx > 1:
            split = 'val'
        else:
            split = 'train' if hash(filename) % 10 != 0 else 'val'
        
        if split == 'train':
            train_count += 1
        else:
            val_count += 1
        
        shutil.copy(img_path, os.path.join(output_dir, 'images', split, filename))
        
        yolo_annotations = []
        img_width = label_data.get('width', 640)
        img_height = label_data.get('height', 480)
        
        for ann in label_data['annotations']:
            class_id = ann.get('class_id', 0)
            
            # Get class name
            class_name = classes_config[class_id]['name'] if class_id < len(classes_config) else f'class_{class_id}'
            
            x_center = (ann['x'] + ann['width'] / 2) / img_width
            y_center = (ann['y'] + ann['height'] / 2) / img_height
            w = ann['width'] / img_width
            h = ann['height'] / img_height
            
            yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
        
        label_txt = filename.rsplit('.', 1)[0] + '.txt'
        with open(os.path.join(output_dir, 'labels', split, label_txt), 'w') as f:
            f.write('\n'.join(yolo_annotations))
        
        exported_count += 1
    
    # Save classes list
    classes_list = [c['name'] for c in classes_config]
    with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
        f.write('\n'.join(classes_list))
    
    # Create data.yaml with correct path
    output_path = output_dir.replace('\\', '/')
    data_yaml_content = f"""path: {output_path}
train: images/train
val: images/val

names:
"""
    for i, cls in enumerate(classes_config):
        data_yaml_content += f"  {i}: {cls['name']}\n"
    
    with open(os.path.join(output_dir, 'data.yaml'), 'w', encoding='utf-8') as f:
        f.write(data_yaml_content)
    
    return jsonify({
        'success': True,
        'output_dir': output_dir,
        'classes': classes_list,
        'message': f'Exported {exported_count} images (Train: {train_count}, Val: {val_count})'
    })

@app.route('/api/classes', methods=['GET'])
def get_classes():
    if DATA_DIR is None:
        return jsonify({'classes': []})
    classes_file = os.path.join(DATA_DIR, 'classes.json')
    if os.path.exists(classes_file):
        with open(classes_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'classes': []})

@app.route('/api/classes', methods=['POST'])
def save_classes():
    if DATA_DIR is None:
        return jsonify({'success': False, 'message': 'No project selected'}), 400
    data = request.json
    classes_file = os.path.join(DATA_DIR, 'classes.json')
    with open(classes_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return jsonify({'success': True})

training_status = {'running': False, 'progress': 0, 'message': ''}

@app.route('/api/train', methods=['POST'])
def start_training():
    global training_status
    
    if training_status['running']:
        return jsonify({'success': False, 'message': 'Training đang chạy!'})
    
    project_name = get_current_project()
    if not project_name:
        return jsonify({'success': False, 'message': 'Chưa có dự án!'}), 400
    
    data = request.json
    model_type = data.get('model', 'yolo26n')
    epochs = int(data.get('epochs', 100))
    img_size = int(data.get('imgSize', 640))
    batch_size = int(data.get('batchSize', 16))
    
    training_status = {
        'running': True, 
        'progress': 0, 
        'message': 'Đang khởi tạo...', 
        'current_epoch': 0, 
        'total_epochs': epochs,
        'project': project_name
    }
    
    import threading
    
    def train_worker():
        global training_status
        try:
            from ultralytics import YOLO
            
            # Dataset và model lưu trong thư mục dự án
            project_runs_dir = os.path.join(PROJECTS_DIR, project_name, 'runs')
            dataset_path = os.path.join(project_runs_dir, 'dataset')
            data_yaml = os.path.join(dataset_path, 'data.yaml')
            
            if not os.path.exists(data_yaml):
                training_status['message'] = f'Lỗi: Dự án "{project_name}" chưa có dataset! Export dữ liệu trước.'
                training_status['running'] = False
                return
            
            training_status['message'] = f'Đang train model cho dự án "{project_name}"...'
            
            model = YOLO(model_type + '.pt')
            
            # Callbacks for progress
            def on_train_epoch_end(trainer):
                global training_status
                training_status['current_epoch'] = trainer.epoch + 1
                training_status['progress'] = int((training_status['current_epoch'] / training_status['total_epochs']) * 100)
                training_status['message'] = f'Epoch {training_status["current_epoch"]}/{training_status["total_epochs"]}'
            
            model.add_callback("on_train_epoch_end", on_train_epoch_end)
            
            # Train với project riêng cho dự án
            results = model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=img_size,
                batch=batch_size,
                project=project_runs_dir,
                name='train',
                exist_ok=True,
                verbose=True,
                device='cpu',
                patience=50,
                save=True,
                amp=False,
            )
            
            # Model lưu trong project runs folder
            best_model = os.path.join(project_runs_dir, 'train', 'weights', 'best.pt')
            
            if os.path.exists(best_model):
                training_status['message'] = f'Train hoàn thành! Model lưu trong dự án "{project_name}"'
            else:
                training_status['message'] = f'Train hoàn thành cho dự án "{project_name}"!'
            
            training_status['progress'] = 100
            training_status['running'] = False
            
        except Exception as e:
            training_status['message'] = f'Lỗi: {str(e)}'
            training_status['running'] = False
    
    thread = threading.Thread(target=train_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': f'Bắt đầu train cho dự án "{project_name}"...'})

@app.route('/api/train/status', methods=['GET'])
def get_training_status():
    return jsonify(training_status)

@app.route('/api/detect/frame', methods=['POST'])
def detect_frame():
    """Detect objects in a frame from camera"""
    global detection_model, detection_model_path
    
    from ultralytics import YOLO
    import numpy as np
    import cv2
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        model_path = data.get('model_path')
        
        if not image_data:
            return jsonify({'error': 'No image data'}), 400
        
        if not model_path:
            return jsonify({'detections': [], 'count': 0, 'message': 'Chưa chọn model!'})
        
        if not os.path.exists(model_path):
            return jsonify({'detections': [], 'count': 0, 'message': f'Model không tìm thấy: {model_path}'})
        
        # Load model - cache để tăng tốc (force CPU for RTX 5050)
        if detection_model is None or detection_model_path != model_path:
            detection_model = YOLO(model_path)
            detection_model_path = model_path
            print(f"[DETECT] Model loaded: {model_path}")
        
        # Decode base64 image
        header, encoded = image_data.split(',', 1) if ',' in image_data else ('', image_data)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Load classes config
        classes_config = []
        classes_file = os.path.join(DATA_DIR, 'classes.json')
        if os.path.exists(classes_file):
            with open(classes_file, 'r') as f:
                classes_config = json.load(f).get('classes', [])
        
        # Run detection - FORCE CPU
        try:
            results = detection_model(img, verbose=False, conf=0.013, iou=0.99, device='cpu')
        except Exception as e:
            print(f"[DETECT] Error: {e}")
            return jsonify({'error': str(e), 'detections': []}), 500
        
        # Parse results
        detections = []
        for r in results:
            boxes = r.boxes
            if len(boxes) == 0:
                print(f"[DETECT] No objects found")
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                
                class_name = str(cls_id)
                class_color = '#ff0000'
                if classes_config and cls_id < len(classes_config):
                    if isinstance(classes_config[cls_id], dict):
                        class_name = classes_config[cls_id].get('name', str(cls_id))
                        class_color = classes_config[cls_id].get('color', '#ff0000')
                    else:
                        class_name = classes_config[cls_id]
                
                print(f"[DETECT] Found: {class_name} conf={conf:.3f} box=({int(x1)},{int(y1)},{int(x2)},{int(y2)})")
                
                detections.append({
                    'x': int(x1),
                    'y': int(y1),
                    'width': int(x2 - x1),
                    'height': int(y2 - y1),
                    'confidence': round(conf, 2),
                    'class_id': cls_id,
                    'class_name': class_name,
                    'color': class_color
                })
        
        return jsonify({
            'detections': detections,
            'count': len(detections)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'detections': []}), 500

@app.route('/api/detect/model', methods=['GET'])
def get_model_info():
    """Get information about available detection model"""
    runs_dir = os.path.join(PROJECT_ROOT, 'runs', 'detect', 'weights')
    best_model = os.path.join(runs_dir, 'best.pt') if os.path.exists(runs_dir) else None
    
    classes_config = []
    classes_file = os.path.join(DATA_DIR, 'classes.json')
    if os.path.exists(classes_file):
        with open(classes_file, 'r') as f:
            classes_config = json.load(f).get('classes', [])
    
    return jsonify({
        'has_model': best_model is not None,
        'model_path': best_model,
        'classes': classes_config
    })

@app.route('/api/detect/models', methods=['GET'])
def get_available_models():
    """Get list of trained models cho dự án hiện tại"""
    models = []
    project_name = get_current_project()
    
    # Lấy models từ thư mục dự án hiện tại
    if project_name:
        runs_dir = os.path.join(PROJECTS_DIR, project_name, 'runs')
    else:
        runs_dir = None
    
    classes_config = []
    classes_file = os.path.join(DATA_DIR, 'classes.json')
    if os.path.exists(classes_file):
        with open(classes_file, 'r') as f:
            classes_config = json.load(f).get('classes', [])
    
    if runs_dir and os.path.exists(runs_dir):
        for exp_dir in os.listdir(runs_dir):
            if exp_dir == 'dataset':
                continue
            weights_dir = os.path.join(runs_dir, exp_dir, 'weights')
            if os.path.exists(weights_dir):
                best_pt = os.path.join(weights_dir, 'best.pt')
                last_pt = os.path.join(weights_dir, 'last.pt')
                
                # Only use .pt files
                if os.path.exists(best_pt):
                    models.append({
                        'name': f'best.pt ({exp_dir})',
                        'path': best_pt,
                        'date': datetime.fromtimestamp(os.path.getctime(best_pt)).strftime('%d/%m/%Y')
                    })
                if os.path.exists(last_pt):
                    models.append({
                        'name': f'last.pt ({exp_dir})',
                        'path': last_pt,
                        'date': datetime.fromtimestamp(os.path.getctime(last_pt)).strftime('%d/%m/%Y')
                    })
    
    models.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        'models': models,
        'classes': classes_config,
        'project_name': project_name
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  YOLO Vision Detection")
    print("=" * 50)
    print(f"  Images folder: {IMAGES_DIR}")
    print(f"  Labels folder: {LABELS_DIR}")
    print(f"  Web UI: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
