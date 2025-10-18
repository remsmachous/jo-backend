import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Reservation, ReservationItem

pytestmark = pytest.mark.django_db
User = get_user_model()

def u(name):  
    return reverse(f"orders:{name}")

def valid_payload():
    return {
        "client": {"nom": "Doe", "prenom": "Jane", "email": "jane@example.com", "telephone": "0600000000"},
        "panier": [
            {"id": "offer_1", "titre": "Solo", "prix": "10.00", "qty": 1},
            {"id": "offer_2", "titre": "Duo",  "prix": "20.00", "qty": 2},
        ],
        "total": "50.00",
        "places": 3,
    }

def test_create_reservation_requires_auth(api_client):
    r = api_client.post(u("reservation_create"), valid_payload(), format="json")
    assert r.status_code in (401, 403)  

def test_create_reservation_ok(api_client):
    user = User.objects.create_user(username="ada", password="S3cure!Pass")
    api_client.force_authenticate(user=user)

    r = api_client.post(u("reservation_create"), valid_payload(), format="json")
    assert r.status_code == 201
    res_id = r.json()["reservation_id"]
    res = Reservation.objects.get(id=res_id)
    assert res.user == user and res.places == 3 and str(res.total) == "50.00"
    
    assert ReservationItem.objects.filter(reservation=res).count() == 2 

def test_create_reservation_rejects_inconsistent_total(api_client):
    user = User.objects.create_user(username="bob", password="S3cure!Pass")
    api_client.force_authenticate(user=user)
    bad = valid_payload()
    bad["total"] = "999.00"  
    r = api_client.post(u("reservation_create"), bad, format="json")
    assert r.status_code in (400, 422)

def test_reservation_detail_is_owner_only(api_client):
    owner = User.objects.create_user(username="owner", password="x")
    other = User.objects.create_user(username="other", password="x")
    api_client.force_authenticate(user=owner)
    r = api_client.post(u("reservation_create"), valid_payload(), format="json")
    rid = r.json()["reservation_id"]
    ok = api_client.get(reverse("orders:reservation_detail", kwargs={"pk": rid}))
    assert ok.status_code == 200  

    api_client.force_authenticate(user=other)
    ko = api_client.get(reverse("orders:reservation_detail", kwargs={"pk": rid}))
    assert ko.status_code in (404, 403)
