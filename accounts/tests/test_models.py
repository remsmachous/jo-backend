# accounts/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


def _make_user_kwargs(i: int):
    """
    Fabrique des kwargs compatibles avec le modèle custom User,
    quelle que soit la valeur de USERNAME_FIELD (email ou username).
    """
    username_field = getattr(User, "USERNAME_FIELD", "username")
    if username_field == "email":
        return {
            "email": f"user{i}@example.com",
            "password": "Aa1234567890!test",  # respecte les validators (longueur/complexité)
            "first_name": f"U{i}",
            "last_name": "Test",
        }
    else:
        # username + email (si le modèle le permet)
        return {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": "Aa1234567890!test",
            "first_name": f"U{i}",
            "last_name": "Test",
        }


class UserAccountKeyTests(TestCase):
    def test_account_key_is_generated_on_create(self):
        """
        A la création d'un user, account_key doit être présente et non vide.
        """
        kwargs = _make_user_kwargs(1)
        password = kwargs.pop("password")
        user = User.objects.create_user(**kwargs, password=password)

        # La clé doit exister et être non vide
        self.assertTrue(
            getattr(user, "account_key", None),
            "account_key devrait être générée à la création de l'utilisateur",
        )
        self.assertIsInstance(user.account_key, str)
        self.assertGreater(len(user.account_key), 0)

    def test_account_key_is_unique_between_users(self):
        """
        Deux users distincts ne doivent pas partager la même account_key.
        """
        # user 1
        kwargs1 = _make_user_kwargs(1)
        pwd1 = kwargs1.pop("password")
        u1 = User.objects.create_user(**kwargs1, password=pwd1)

        # user 2
        kwargs2 = _make_user_kwargs(2)
        pwd2 = kwargs2.pop("password")
        u2 = User.objects.create_user(**kwargs2, password=pwd2)

        self.assertNotEqual(
            u1.account_key, u2.account_key,
            "Deux utilisateurs ne doivent pas avoir la même account_key"
        )
