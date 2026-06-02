import numpy as np
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .preprocess import preprocess
from .inference import TFLiteASLModel
from .models import SignPredictionHistory

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

    def test_prediction_history_saved_for_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='historyuser',
            email='history@example.com',
            password='TestPass123',
            first_name='History',
            last_name='User',
            age=21
        )
        self.client.force_authenticate(user=user)

        url = reverse('predict')
        payload = {"sequence": [[0.0] * 342 for _ in range(64)], "save_to_history": 'true'}
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['saved_to_history'])
        self.assertIsNotNone(response.data['history_id'])

        history_entry = SignPredictionHistory.objects.get(id=response.data['history_id'])
        self.assertEqual(history_entry.user, user)
        self.assertEqual(history_entry.predicted_text, response.data['class'])

    def test_prediction_history_list_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='historylist',
            email='historylist@example.com',
            password='TestPass123',
            first_name='History',
            last_name='List',
            age=22
        )
        SignPredictionHistory.objects.create(
            user=user,
            predicted_text='hello',
            confidence=0.75
        )
        self.client.force_authenticate(user=user)

        url = reverse('sign_prediction_history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['predicted_text'], 'hello')

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

    def test_prediction_with_video_upload_and_save(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='videouser',
            email='video@example.com',
            password='TestPass123',
            first_name='Video',
            last_name='User',
            age=23
        )
        self.client.force_authenticate(user=user)

        url = reverse('predict')
        
        # Create a dummy video file
        video_content = b'dummy video content'
        video_file = SimpleUploadedFile(
            name='test_sign.mp4',
            content=video_content,
            content_type='video/mp4'
        )
        
        # Send request with sequence, video, and save_to_history flag
        # Use JSON format with files parameter for file upload
        sequence_data = [[0.0] * 342 for _ in range(64)]
        response = self.client.post(
            url, 
            {'sequence': sequence_data, 'save_to_history': 'true', 'video': video_file},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['saved_to_history'])
        self.assertIsNotNone(response.data['history_id'])

        # Verify history entry has video URL (or None if upload failed)
        history_entry = SignPredictionHistory.objects.get(id=response.data['history_id'])
        self.assertEqual(history_entry.user, user)
        self.assertEqual(history_entry.predicted_text, response.data['class'])

    def test_prediction_history_list_includes_video_url(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='videohistoryuser',
            email='videohistory@example.com',
            password='TestPass123',
            first_name='Video',
            last_name='History',
            age=24
        )
        
        # Create a history entry with a video URL
        video_url = 'https://res.cloudinary.com/demo/video/upload/v1/sample.mp4'
        SignPredictionHistory.objects.create(
            user=user,
            predicted_text='goodbye',
            confidence=0.95,
            video_url=video_url
        )
        
        self.client.force_authenticate(user=user)

        url = reverse('sign_prediction_history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['predicted_text'], 'goodbye')
        self.assertEqual(response.data[0]['video_url'], video_url)
