import cv2
import numpy as np
from modules.utils import crop_utils
from pipeline import Pipeline
from flask import jsonify
import traceback
import os

class PipelineService(Pipeline):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.recording_frames = []
        # 确保 data/knn 目录存在
        self.knn_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'knn')
        os.makedirs(self.knn_dir, exist_ok=True)
        # 确保加载KNN数据库
        ret = self.translator_manager.load_knn_database()
        if ret:
            print("KNN Database loaded:")
            print(f"Database location: {self.knn_dir}")
            print(f"Available gestures: {sorted(os.listdir(self.knn_dir))}")
            print(f"Total samples: {len(self.translator_manager.knn_labels)}")
        else:
            print("Warning: No KNN database loaded")
        
    def process_frame(self, frame):
        # 首先裁剪成正方形
        frame = crop_utils.crop_square(frame)
        
        # 然后调整到合适的大小
        target_size = 640  # 或其他合适的尺寸
        frame = cv2.resize(frame, (target_size, target_size))
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 使用父类的update方法处理帧
        self.update(frame_rgb)
        
        # 如果正在录制，保存处理后的数据
        if self.is_recording:
            self.recording_frames.append({
                "pose": self.pose_history[-1] if len(self.pose_history) > 0 else None,
                "face": self.face_history[-1] if len(self.face_history) > 0 else None,
                "lh": self.lh_history[-1] if len(self.lh_history) > 0 else None,
                "rh": self.rh_history[-1] if len(self.rh_history) > 0 else None
            })
        
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
    def handle_recording(self):
        """处理录制请求"""
        try:
            if not self.is_recording:  # 开始录制
                self.is_recording = True
                self.recording_frames = []
                print("Started recording")
                return jsonify({"status": "started"}), 200
            else:  # 停止录制
                self.is_recording = False
                if len(self.recording_frames) < 16:
                    print(f"Recording too short: {len(self.recording_frames)} frames")
                    return jsonify({"error": "Recording too short"}), 400
                
                print(f"Processing {len(self.recording_frames)} frames")
                try:
                    poses = [f["pose"] for f in self.recording_frames if f["pose"] is not None]
                    faces = [f["face"] for f in self.recording_frames if f["face"] is not None]
                    lhs = [f["lh"] for f in self.recording_frames if f["lh"] is not None]
                    rhs = [f["rh"] for f in self.recording_frames if f["rh"] is not None]
                    
                    if not (poses and faces and lhs and rhs):
                        raise ValueError("Missing required pose data")
                    
                    vid_res = {
                        "pose_frames": np.stack(poses),
                        "face_frames": np.stack(faces),
                        "lh_frames": np.stack(lhs),
                        "rh_frames": np.stack(rhs),
                        "n_frames": len(self.recording_frames)
                    }
                    
                    # 获取特征
                    self.current_features = self.translator_manager.get_feats(vid_res)
                    print("Features shape:", self.current_features.shape)
                    self.reset_pipeline()
                    
                    return jsonify({"status": "completed"}), 200
                    
                except Exception as e:
                    print(f"Error processing recording: {str(e)}")
                    print(traceback.format_exc())
                    return jsonify({"error": f"Error processing recording: {str(e)}"}), 500
                
        except Exception as e:
            print(f"Recording error: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
    
    def save_recording(self, gloss_name):
        """保存录制的样本"""
        try:
            if not hasattr(self, 'current_features'):
                return jsonify({"error": "No recording available"}), 400
            
            print(f"Saving features for {gloss_name}, shape:", self.current_features.shape)
            
            # 确保特征是正确的形状
            if len(self.current_features.shape) != 1:
                print("Reshaping features...")
                self.current_features = self.current_features.flatten()
                
            self.translator_manager.save_knn_database(gloss_name, [self.current_features])
            
            # 保存后立即重新加载数据库
            if self.translator_manager.load_knn_database():
                print("Database reloaded successfully")
                print("Current database size:", len(self.translator_manager.knn_labels) if hasattr(self.translator_manager, 'knn_labels') else 0)
            else:
                print("Failed to reload database")
                
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            print(f"Save error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
        
    def translate_recording(self):
        """处理翻译请求"""
        try:
            if not hasattr(self, 'current_features'):
                print("No current_features found")
                return jsonify({"error": "No recording available"}), 400
                
            # 检查KNN数据库是否已加载
            if not hasattr(self.translator_manager, 'knn_feats') or len(self.translator_manager.knn_feats) == 0:
                print("KNN database is empty, trying to reload...")
                if not self.translator_manager.load_knn_database():
                    return jsonify({"error": "No KNN samples available"}), 400
            
            # 打印更多调试信息
            print("Current features shape:", self.current_features.shape)
            print("KNN database shape:", self.translator_manager.knn_feats.shape if hasattr(self.translator_manager, 'knn_feats') else "No KNN feats")
            print("KNN labels:", self.translator_manager.knn_labels if hasattr(self.translator_manager, 'knn_labels') else "No KNN labels")
            
            # 运行翻译器
            result = self.translator_manager.run_knn(self.current_features)
            print("Translation result:", result)
            
            if not result:
                return jsonify({"error": "No translation result"}), 400
                
            return jsonify({
                "status": "success",
                "text": result
            }), 200
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500 
        
    def handle_error(error):
        print(f"Route error: {str(error)}")
        return jsonify({"error": str(error)}), 500

    def gen_frames(self):
        try:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                processed_frame = self.process_frame(frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                frame = buffer.tobytes()
                
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Video stream error: {str(e)}")
            raise