import eventlet
eventlet.monkey_patch()

import json
import os
import subprocess

import cv2
import numpy as np
import requests
from flask import Flask, Response, request
from flask_socketio import SocketIO, emit
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

from predict import predictImg


class VideoProcessingApp:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = os.getenv('FLASK_HOST', host)
        self.port = int(os.getenv('FLASK_PORT', port))
        self.spring_api_base_url = self.normalize_base_url(
            os.getenv('SPRING_API_BASE_URL', 'http://127.0.0.1:9999')
        )
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins='*', async_mode='eventlet')
        self.setup_routes()
        self.data = {}
        self.paths = {
            'download': './runs/video/download.mp4',
            'output': './runs/video/output.mp4',
            'camera_output': './runs/video/camera_output.avi',
            'video_output': './runs/video/camera_output.avi',
        }
        self.recording = False

    def get_overlay_font(self, size=18):
        font_candidates = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/msyhbd.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/arphic/ukai.ttc',
        ]
        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size=size)
                except OSError:
                    continue
        return ImageFont.load_default()

    def setup_routes(self):
        self.app.add_url_rule('/file_names', 'file_names', self.file_names, methods=['GET'])
        self.app.add_url_rule('/predictImg', 'predictImg', self.predictImg, methods=['POST'])
        self.app.add_url_rule('/predictVideo', 'predictVideo', self.predictVideo)
        self.app.add_url_rule('/predictCamera', 'predictCamera', self.predictCamera)
        self.app.add_url_rule('/stopCamera', 'stopCamera', self.stopCamera, methods=['GET'])

        @self.socketio.on('connect')
        def handle_connect():
            print('WebSocket connected')
            emit('message', {'data': 'Socket connected'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('WebSocket disconnected')

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

    def file_names(self):
        weight_items = [{'value': name, 'label': name} for name in self.get_file_names('./weights')]
        return json.dumps({'weight_items': weight_items})

    def predictImg(self):
        data = request.get_json()
        self.data.clear()
        self.data.update(
            {
                'username': data['username'],
                'weight': data['weight'],
                'conf': data['conf'],
                'startTime': data['startTime'],
                'inputImg': data['inputImg'],
                'kind': data['kind'],
            }
        )
        predictor = predictImg.ImagePredictor(
            weights_path=f'./weights/{self.data["weight"]}',
            img_path=self.data['inputImg'],
            save_path='./runs/result.jpg',
            kind=self.data['kind'],
            conf=float(self.data['conf']),
        )
        results = predictor.predict()
        uploaded_url = self.upload('./runs/result.jpg')
        if results['labels'] != 'prediction_failed':
            self.data['status'] = 200
            self.data['message'] = 'prediction_success'
            self.data['outImg'] = uploaded_url
            self.data['allTime'] = results['allTime']
            self.data['confidence'] = json.dumps(results['confidences'])
            self.data['label'] = json.dumps(results['labels'])
        else:
            self.data['status'] = 400
            self.data['message'] = 'prediction_failed'
        path = self.data['inputImg'].split('/')[-1]
        if os.path.exists('./' + path):
            os.remove('./' + path)
        return json.dumps(self.data, ensure_ascii=False)

    def predictVideo(self):
        self.data.clear()
        self.data.update(
            {
                'username': request.args.get('username'),
                'weight': request.args.get('weight'),
                'conf': request.args.get('conf'),
                'startTime': request.args.get('startTime'),
                'inputVideo': request.args.get('inputVideo'),
                'kind': request.args.get('kind'),
                'frameResults': '[]',
            }
        )
        self.download(self.data['inputVideo'], self.paths['download'])
        cap = cv2.VideoCapture(self.paths['download'])
        if not cap.isOpened():
            raise ValueError('can_not_open_video')
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        frame_index = 0
        frame_results = []

        video_writer = cv2.VideoWriter(
            self.paths['video_output'],
            cv2.VideoWriter_fourcc(*'XVID'),
            fps,
            (640, 480),
        )
        model = YOLO(f'./weights/{self.data["weight"]}')

        def generate():
            nonlocal frame_index
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.resize(frame, (640, 480))
                    results = model.predict(source=frame, conf=float(self.data['conf']), show=False)
                    processed_frame = results[0].plot()
                    frame_result = self.build_frame_result(results[0], frame_index, fps)
                    processed_frame = self.draw_frame_overlay(processed_frame, frame_result)
                    frame_results.append(frame_result)
                    self.socketio.emit('frame_result', {'data': {**frame_result, 'source': 'video'}})
                    self.socketio.sleep(0)
                    video_writer.write(processed_frame)
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    frame_index += 1
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': 'video_processing_finished'})
                for progress in self.convert_avi_to_mp4(self.paths['video_output']):
                    self.socketio.emit('progress', {'data': progress})
                uploaded_url = self.upload(self.paths['output'])
                self.data['outVideo'] = uploaded_url
                self.data['frameResults'] = json.dumps(frame_results, ensure_ascii=False)
                self.save_data(json.dumps(self.data), f'{self.spring_api_base_url}/videoRecords')
                self.cleanup_files([self.paths['download'], self.paths['output'], self.paths['video_output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def predictCamera(self):
        self.data.clear()
        self.data.update(
            {
                'username': request.args.get('username'),
                'weight': request.args.get('weight'),
                'kind': request.args.get('kind'),
                'conf': request.args.get('conf'),
                'startTime': request.args.get('startTime'),
                'frameResults': '[]',
            }
        )
        self.socketio.emit('message', {'data': 'camera_loading'})
        model = YOLO(f'./weights/{self.data["weight"]}')
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        fps = 20
        frame_index = 0
        frame_results = []
        video_writer = cv2.VideoWriter(self.paths['camera_output'], cv2.VideoWriter_fourcc(*'XVID'), fps, (640, 480))
        self.recording = True

        def generate():
            nonlocal frame_index
            try:
                while self.recording:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model.predict(source=frame, imgsz=640, conf=float(self.data['conf']), show=False)
                    processed_frame = results[0].plot()
                    frame_result = self.build_frame_result(results[0], frame_index, fps)
                    processed_frame = self.draw_frame_overlay(processed_frame, frame_result)
                    frame_results.append(frame_result)
                    self.socketio.emit('frame_result', {'data': {**frame_result, 'source': 'camera'}})
                    self.socketio.sleep(0)
                    if self.recording and video_writer:
                        video_writer.write(processed_frame)
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    frame_index += 1
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': 'camera_processing_finished'})
                for progress in self.convert_avi_to_mp4(self.paths['camera_output']):
                    self.socketio.emit('progress', {'data': progress})
                uploaded_url = self.upload(self.paths['output'])
                self.data['outVideo'] = uploaded_url
                self.data['frameResults'] = json.dumps(frame_results, ensure_ascii=False)
                self.save_data(json.dumps(self.data), f'{self.spring_api_base_url}/cameraRecords')
                self.cleanup_files([self.paths['download'], self.paths['output'], self.paths['camera_output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stopCamera(self):
        self.recording = False
        return json.dumps({'status': 200, 'message': 'ok', 'code': 0})

    def save_data(self, data, path):
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(path, data=data, headers=headers)
            if response.status_code == 200:
                print('record_saved')
            else:
                print(f'record_save_failed: {response.status_code}')
        except requests.RequestException as exc:
            print(f'save_data_error: {str(exc)}')

    def build_frame_result(self, result, frame_index, fps):
        boxes = result.boxes
        names = result.names
        detections = []
        label_summary = {}

        if boxes is not None and boxes.cls is not None:
            cls_list = boxes.cls.tolist()
            conf_list = boxes.conf.tolist() if boxes.conf is not None else []
            xyxy_list = boxes.xyxy.tolist() if boxes.xyxy is not None else []
            for index, cls_id in enumerate(cls_list):
                label = str(names.get(int(cls_id), int(cls_id)))
                confidence = round(float(conf_list[index]) if index < len(conf_list) else 0, 4)
                box = xyxy_list[index] if index < len(xyxy_list) else []
                detections.append(
                    {
                        'label': label,
                        'confidence': confidence,
                        'box': [round(float(item), 2) for item in box] if box else [],
                    }
                )
                if label not in label_summary or confidence > label_summary[label]:
                    label_summary[label] = confidence

        top_labels = [
            {'label': label, 'confidence': confidence}
            for label, confidence in sorted(label_summary.items(), key=lambda item: item[1], reverse=True)
        ]
        timestamp_seconds = round(frame_index / fps, 3) if fps else 0
        return {
            'frameIndex': frame_index,
            'timestamp': self.format_timestamp(timestamp_seconds),
            'timestampSeconds': timestamp_seconds,
            'detectionCount': len(detections),
            'labels': [item['label'] for item in top_labels],
            'topLabels': top_labels,
            'detections': detections,
            'summaryText': '未检测到病虫害'
            if not top_labels
            else ' | '.join([f"{item['label']}({item['confidence'] * 100:.1f}%)" for item in top_labels]),
        }

    def format_timestamp(self, seconds):
        total_milliseconds = int(round(seconds * 1000))
        hours, remainder = divmod(total_milliseconds, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        secs, milliseconds = divmod(remainder, 1000)
        return f'{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}'

    def draw_frame_overlay(self, frame, frame_result):
        lines = [
            f"TIME  {frame_result.get('timestamp', '--:--:--.---')}",
            f"FRAME {frame_result.get('frameIndex', 0)}",
            f"RESULT {self.compact_summary(frame_result)}",
        ]
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        draw = ImageDraw.Draw(image, 'RGBA')
        font = self.get_overlay_font(size=18)
        padding_x = 12
        padding_y = 10
        line_gap = 8
        origin_x = 16
        origin_y = 16
        max_width = 0
        line_heights = []

        for line in lines:
            left, top, right, bottom = draw.textbbox((0, 0), line[:60], font=font)
            max_width = max(max_width, right - left)
            line_heights.append(bottom - top)

        box_width = min(max_width + padding_x * 2, frame.shape[1] - 24)
        box_height = padding_y * 2 + sum(line_heights) + line_gap * (len(lines) - 1)
        draw.rounded_rectangle(
            (origin_x, origin_y, origin_x + box_width, origin_y + box_height),
            radius=12,
            fill=(18, 34, 46, 165),
        )

        current_y = origin_y + padding_y
        for index, line in enumerate(lines):
            draw.text((origin_x + padding_x, current_y), line[:60], font=font, fill=(245, 248, 250, 255))
            current_y += line_heights[index] + line_gap

        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def compact_summary(self, frame_result):
        top_labels = frame_result.get('topLabels') or []
        if not top_labels:
            return 'no detection'
        parts = [f"{item['label']} {item['confidence'] * 100:.1f}%" for item in top_labels[:2]]
        return ' | '.join(parts)

    def convert_avi_to_mp4(self, temp_output):
        ffmpeg_command = f'ffmpeg -i {temp_output} -vcodec libx264 {self.paths["output"]} -y'
        process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        total_duration = self.get_video_duration(temp_output)

        for line in process.stderr:
            if 'time=' in line:
                try:
                    time_str = line.split('time=')[1].split(' ')[0]
                    h, m, s = map(float, time_str.split(':'))
                    processed_time = h * 3600 + m * 60 + s
                    if total_duration > 0:
                        progress = (processed_time / total_duration) * 100
                        yield progress
                except Exception as exc:
                    print(f'progress_parse_error: {exc}')

        process.wait()
        yield 100

    def get_video_duration(self, path):
        try:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            return total_frames / fps if fps > 0 else 0
        except Exception:
            return 0

    def get_file_names(self, directory):
        try:
            return [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
        except Exception as exc:
            print(f'get_file_names_error: {exc}')
            return []

    def upload(self, out_path):
        upload_url = f'{self.spring_api_base_url}/files/upload'
        try:
            with open(out_path, 'rb') as file:
                files = {'file': (os.path.basename(out_path), file)}
                response = requests.post(upload_url, files=files)
                if response.status_code == 200:
                    return response.json()['data']
                print(f'upload_failed: {response.status_code}')
        except Exception as exc:
            print(f'upload_error: {str(exc)}')
        return ''

    def download(self, url, save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
        except requests.RequestException as exc:
            print(f'download_error: {exc}')

    def cleanup_files(self, file_paths):
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

    def cleanup_resources(self, cap, video_writer):
        if cap.isOpened():
            cap.release()
        if video_writer is not None:
            video_writer.release()
        cv2.destroyAllWindows()

    @staticmethod
    def normalize_base_url(url):
        return url.rstrip('/')


if __name__ == '__main__':
    video_app = VideoProcessingApp()
    video_app.run()
