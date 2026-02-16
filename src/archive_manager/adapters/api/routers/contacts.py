#!/usr/bin/env python3
"""Contacts HTTP endpoints."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status

from archive_manager.adapters.api.deps import get_contact_service
from archive_manager.adapters.api.schemas import (
    ContactCreateRequest,
    ContactPageResponse,
    ContactResponse,
    ContactUpdateRequest,
)
from archive_manager.application.dto import ContactDTO, ContactPageDTO
from archive_manager.application.services import ContactService
from archive_manager.core.errors import AppWarning

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreateRequest,
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """Create a contact.

    Args:
        payload: Contact creation payload.
        service: Injected contact service.

    Returns:
        Created contact response.
    """
    dto = ContactDTO(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
    )
    contact = service.create(
        first_name=dto.first_name,
        last_name=dto.last_name,
        email=dto.email,
        phone=dto.phone,
    )
    return ContactResponse.from_dto(ContactDTO.from_entity(contact))


@router.get("", response_model=ContactPageResponse)
def list_contacts(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, description="Items per page"),
    service: ContactService = Depends(get_contact_service),
) -> ContactPageResponse:
    """List contacts with page-based pagination.

    Args:
        page: 1-based page number.
        limit: Requested page size (default 20).
        service: Injected contact service.

    Returns:
        Paginated contacts response.
    """
    offset = (page - 1) * limit
    try:
        result = service.list_contacts(limit=limit, offset=offset)
        dto = ContactPageDTO(
            contacts=[ContactDTO.from_entity(c) for c in result.contacts],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
        )
        return ContactPageResponse.from_dto(dto)
    except AppWarning as exc:
        if exc.code != "EMPTY_CONTACT_LIST":
            raise
        dto = ContactPageDTO(contacts=[], total=0, limit=limit, offset=0)
        return ContactPageResponse.from_dto(dto)


@router.get("/search/name", response_model=list[ContactResponse])
def search_by_name(
    full_name: str = Query(min_length=1),
    service: ContactService = Depends(get_contact_service),
) -> Sequence[ContactResponse]:
    """Search contacts by full name.

    Args:
        full_name: Name fragment to search.
        service: Injected contact service.

    Returns:
        Matching contacts. Returns empty list when no results are found.
    """
    try:
        contacts = service.find_by_name(full_name)
        return [ContactResponse.from_dto(ContactDTO.from_entity(c)) for c in contacts]
    except AppWarning as exc:
        if exc.code != "CONTACT_NOT_FOUND":
            raise
        return []


@router.get("/search/email", response_model=ContactResponse)
def search_by_email(
    email: str = Query(min_length=1),
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """Search contact by exact email.

    Args:
        email: Email address.
        service: Injected contact service.

    Returns:
        Matching contact.

    Raises:
        HTTPException: If contact is not found.
    """
    try:
        contact = service.find_by_email(email)
        return ContactResponse.from_dto(ContactDTO.from_entity(contact))
    except AppWarning as exc:
        if exc.code != "CONTACT_NOT_FOUND":
            raise
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        ) from exc


@router.get("/search/phone", response_model=ContactResponse)
def search_by_phone(
    phone: str = Query(min_length=1),
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """Search contact by exact phone.

    Args:
        phone: Phone number.
        service: Injected contact service.

    Returns:
        Matching contact.

    Raises:
        HTTPException: If contact is not found.
    """
    try:
        contact = service.find_by_phone(phone)
        return ContactResponse.from_dto(ContactDTO.from_entity(contact))
    except AppWarning as exc:
        if exc.code != "CONTACT_NOT_FOUND":
            raise
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        ) from exc


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """Get a contact by ID.

    Args:
        contact_id: Contact identifier.
        service: Injected contact service.

    Returns:
        The requested contact.

    Raises:
        HTTPException: If contact is not found.
    """
    try:
        contact = service.get(contact_id)
        return ContactResponse.from_dto(ContactDTO.from_entity(contact))
    except AppWarning as exc:
        if exc.code != "CONTACT_NOT_FOUND":
            raise
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        ) from exc


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    payload: ContactUpdateRequest,
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """Update an existing contact.

    Args:
        contact_id: Target contact ID.
        payload: New contact payload.
        service: Injected contact service.

    Returns:
        Updated contact response.
    """
    updated = service.update(
        contact_id=contact_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
    )
    return ContactResponse.from_dto(ContactDTO.from_entity(updated))


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
) -> None:
    """Soft-delete a contact.

    Args:
        contact_id: Target contact ID.
        service: Injected contact service.

    Raises:
        HTTPException: If contact does not exist.
    """
    deleted = service.delete(contact_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
