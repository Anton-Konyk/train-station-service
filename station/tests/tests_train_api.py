import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Train, Facility, TrainType
from station.serializers import TrainListSerializer, TrainRetrieveSerializer

TRAIN_URL = reverse("station:train-list")
TRAIN_TYPE_URL = reverse("station:traintype-list")


def sample_train_type(**params):
    defaults = {
            "name": "Test_AVE202",
    }
    defaults.update(params)
    if TrainType.objects.filter(**defaults).exists():
        return TrainType.objects.get(**defaults)
    return TrainType.objects.create(**defaults)


def sample_train(**params) -> Train:
    train_type = params.get("train_type", sample_train_type())
    defaults = {
        "number": 99001,
        "cargo_num": 5,
        "places_in_cargo": 30,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])


def image_upload_url(train_types_id):
    """Return URL for recipe image upload"""
    return reverse("station:traintype-upload-image", args=[train_types_id])


def detail_train_types_url(train_types_id):
    return reverse("station:traintype-detail", args=[train_types_id])


class TrainTypeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "pass_word12"
        )
        self.client.force_authenticate(self.user)
        self.train_type = sample_train_type()

    def tearDown(self):
        self.train_type.image.delete()

    def test_upload_image_to_train_type(self):
        """Test uploading an image to train_type"""
        url = image_upload_url(self.train_type.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.train_type.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train_type.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.train_type.id)
        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_train_type_list(self):
        url = TRAIN_TYPE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Test_AVG",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train_type = TrainType.objects.get(name="Test_AVG")
        self.assertFalse(train_type.image)

    def test_image_url_is_shown_on_train_type_detail(self):
        url = image_upload_url(self.train_type.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                url,
                {
                    "name": "Test_AVG",
                    "image": ntf,
                },
                format="multipart",
            )
        res = self.client.get(detail_train_types_url(self.train_type.id))
        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_train_type_list(self):
        url = image_upload_url(self.train_type.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                url,
                {
                    "name": "Test_AVG",
                    "image": ntf,
                },
                format="multipart",
            )
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertIn("image", res.data[0].keys())


class UnauthenticatedTrainApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)  # logining test user

    def test_train_list(self):
        train_with_facilities = sample_train()
        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="WC")
        train_with_facilities.facilities.add(facility_1, facility_2)
        res = self.client.get(TRAIN_URL)
        trains = Train.objects.all()
        serializer = TrainListSerializer(trains, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_buses_by_facilities(self):
        train_without_facility = sample_train(number=90001)
        train_with_facility_1 = sample_train(number=90002)
        train_with_facility_2 = sample_train(number=90003)
        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="WC")
        train_with_facility_1.facilities.add(facility_1)
        train_with_facility_2.facilities.add(facility_2)
        res = self.client.get(
            TRAIN_URL,
            {"facilities": f"{facility_1.id}, {facility_2.id}"}
        )
        serializer_without_facilities = (
            TrainListSerializer(train_without_facility))
        print(serializer_without_facilities.data)
        serializer_train_facility_1 = (
            TrainListSerializer(train_with_facility_1))
        serializer_train_with_facility_2_facility_2 = (
            TrainListSerializer(train_with_facility_2))
        self.assertIn(
            serializer_train_facility_1.data,
            res.data["results"]
        )
        self.assertIn(
            serializer_train_with_facility_2_facility_2.data,
            res.data["results"]
        )
        self.assertNotIn(
            serializer_without_facilities.data,
            res.data["results"]
        )

    def test_retrieve_train_detail(self):
        train = sample_train()
        train.facilities.add(Facility.objects.create(name="WiFi"))
        url = detail_url(train.id)
        res = self.client.get(url)
        serializer = TrainRetrieveSerializer(train)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        payload = {
            "number": 99009,
            "cargo_num": 4,
            "places_in_cargo": 30,
            "train_type": [
                {
                    "id": 1,
                    "name": "AVE",
                    "image": "http://127.0.0.1:8000/"
                             "media/uploads/train/ave-52e2dac4-"
                             "fec0-4a6e-b907-9d4256b6248a.webp"
                }
            ],
            "facilities": [
                {
                    "id": 1,
                    "name": "Coffe for free"
                }
            ]
        }
        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
