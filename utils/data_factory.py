"""Test data factories — every scenario gets isolated, generated data."""
from __future__ import annotations

from dataclasses import dataclass

from faker import Faker

fake = Faker()


@dataclass(frozen=True)
class UserAccount:
    email: str
    password: str


def make_user() -> UserAccount:
    return UserAccount(email=fake.unique.email(), password=fake.password(length=12))
