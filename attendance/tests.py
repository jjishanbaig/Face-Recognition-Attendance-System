from django.test import SimpleTestCase

from .face_engine import detector


class FaceEngineTests(SimpleTestCase):
    def test_detector_loads_frontal_face_cascade(self):
        self.assertFalse(detector().empty())
