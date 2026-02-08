#!/usr/bin/env python3
"""Base ORM model for all database entities."""

from sqlalchemy.orm import DeclarativeBase


class BaseORM(DeclarativeBase):
    """Shared declarative base for all ORM models."""
