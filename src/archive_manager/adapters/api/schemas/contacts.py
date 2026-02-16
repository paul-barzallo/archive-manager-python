#!/usr/bin/env python3
"""Contact-specific Pydantic schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from archive_manager.application.dto import ContactDTO, ContactPageDTO


class ContactCreateRequest(BaseModel):
    """Payload used to create a contact."""

    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    phone: str = ""


class ContactUpdateRequest(ContactCreateRequest):
    """Payload used to update a contact."""


class ContactResponse(BaseModel):
    """Contact response payload."""

    model_config = ConfigDict(from_attributes=True)

    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone: str

    @classmethod
    def from_dto(cls, dto: ContactDTO) -> ContactResponse:
        """Create response schema from a contact DTO.

        Args:
            dto: Contact data transfer object.

        Returns:
            Contact response model.
        """
        return cls(
            contact_id=dto.contact_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            phone=dto.phone,
        )


class ContactPageResponse(BaseModel):
    """Paginated contacts response payload."""

    contacts: list[ContactResponse]
    total: int
    limit: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def from_dto(cls, dto: ContactPageDTO) -> ContactPageResponse:
        """Create paginated response schema from a page DTO.

        Args:
            dto: Paginated contacts DTO.

        Returns:
            Paginated response model.
        """
        return cls(
            contacts=[ContactResponse.from_dto(item) for item in dto.contacts],
            total=dto.total,
            limit=dto.limit,
            current_page=dto.current_page,
            total_pages=dto.total_pages,
            has_next=dto.has_next,
            has_previous=dto.has_previous,
        )
