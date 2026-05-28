import numpy as np
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .preprocess import preprocess
from .inference import TFLiteASLModel

class ASLInferenceTests(APITestCase):

    def test_preprocessing_shape(self):
        # Create a dummy raw landmark sequence of shape (64, 114, 3)
        dummy_seq = np.random.rand(64, 114, 3).astype(np.float32)
        
        # Run preprocessing
        processed = preprocess(dummy_seq)
        
        # Verify that output shape is exactly (64, 1026) as expected by the model
        self.assertEqual(processed.shape, (64, 1026))
        self.assertEqual(processed.dtype, np.float32)

    def test_model_singleton_prediction(self):
        # Get instance of model
        model = TFLiteASLModel.get_instance()
        self.assertIsNotNone(model)
        
        # Run mock prediction on dummy preprocessed data
        dummy_processed = np.zeros((64, 1026), dtype=np.float32)
        predicted_word, confidence = model.predict(dummy_processed)
        
        # Check that outputs are mapped
        self.assertIsInstance(predicted_word, str)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0.0 <= confidence <= 1.0)

    def test_prediction_endpoint_success(self):
        # Generate dummy payload representing a valid sequence (64 frames, 342 coordinates each)
        dummy_sequence = [[0.0] * 342 for _ in range(64)]
        
        url = reverse('predict')
        payload = {"sequence": dummy_sequence}
        
        response = self.client.post(url, payload, format='json')
        
        # Verify status and fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('class', response.data)
        self.assertIn('confidence', response.data)
        self.assertIsInstance(response.data['class'], str)
        self.assertIsInstance(response.data['confidence'], float)

    def test_prediction_endpoint_missing_sequence(self):
        url = reverse('predict')
        payload = {}
        
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_prediction_endpoint_invalid_shape(self):
        url = reverse('predict')
        
        # Invalid shape sequence (e.g. only 60 frames)
        invalid_sequence = [[0.0] * 342 for _ in range(60)]
        payload = {"sequence": invalid_sequence}
        
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
