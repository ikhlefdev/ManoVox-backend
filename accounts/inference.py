import os
import json
import numpy as np
import tensorflow as tf
from django.conf import settings

class TFLiteASLModel:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Path to model file in the Django project root directory
        model_path = os.path.join(settings.BASE_DIR, 'asl_50words.tflite')
        
        # Load TFLite Interpreter
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Cache input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load label map
        labels_path = os.path.join(settings.BASE_DIR, 'accounts', 'data', 'label_map.json')
        with open(labels_path, 'r', encoding='utf-8') as f:
            self.label_map = {int(k): v for k, v in json.load(f).items()}

    def predict(self, preprocessed_seq: np.ndarray):
        """
        preprocessed_seq: np.ndarray of shape (64, 1026)
        """
        # Add batch dimension to match expected shape [1, 64, 1026]
        input_data = np.expand_dims(preprocessed_seq, axis=0).astype(np.float32)
        
        # Set the input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get raw output logits of shape [1, 50]
        logits = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        
        # Apply Softmax for probability distribution (model outputs logits)
        exp_logits = np.exp(logits - np.max(logits))  # Subtract max for numerical stability
        probs = exp_logits / np.sum(exp_logits)
        
        # Find highest probability index
        cls_idx = int(np.argmax(probs))
        confidence = float(probs[cls_idx])
        
        return self.label_map[cls_idx], confidence
