-- =============================================================================
-- Defensive triggers for the contacts table
-- =============================================================================
-- Business-logic validation (format, length, regex) is handled by the
-- application layer (ContactValidator / ContactPolicy).
-- These triggers are a last line of defense for data integrity.
-- =============================================================================

-- 1. Auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS trg_contacts_updated_at
AFTER UPDATE ON contacts
FOR EACH ROW
BEGIN
    UPDATE contacts SET updated_at = datetime('now')
    WHERE id = NEW.id;
END;

-- 2. Prevent empty required fields on INSERT
CREATE TRIGGER IF NOT EXISTS trg_contacts_required_fields_insert
BEFORE INSERT ON contacts
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'first_name is required')
    WHERE NEW.first_name IS NULL OR TRIM(NEW.first_name) = '';
    SELECT RAISE(ABORT, 'last_name is required')
    WHERE NEW.last_name IS NULL OR TRIM(NEW.last_name) = '';
    SELECT RAISE(ABORT, 'email is required')
    WHERE NEW.email IS NULL OR TRIM(NEW.email) = '';
    -- E.164: phone digits (excluding '+') must be between 7 and 15
    SELECT RAISE(ABORT, 'phone exceeds E.164 maximum of 15 digits')
    WHERE NEW.phone != '' AND LENGTH(REPLACE(NEW.phone, '+', '')) > 15;
    SELECT RAISE(ABORT, 'phone below E.164 minimum of 7 digits')
    WHERE NEW.phone != '' AND LENGTH(REPLACE(NEW.phone, '+', '')) < 7;
END;

-- 3. Prevent empty required fields on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_contacts_required_fields_update
BEFORE UPDATE ON contacts
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'first_name is required')
    WHERE NEW.first_name IS NULL OR TRIM(NEW.first_name) = '';
    SELECT RAISE(ABORT, 'last_name is required')
    WHERE NEW.last_name IS NULL OR TRIM(NEW.last_name) = '';
    SELECT RAISE(ABORT, 'email is required')
    WHERE NEW.email IS NULL OR TRIM(NEW.email) = '';
    -- E.164: phone digits (excluding '+') must be between 7 and 15
    SELECT RAISE(ABORT, 'phone exceeds E.164 maximum of 15 digits')
    WHERE NEW.phone != '' AND LENGTH(REPLACE(NEW.phone, '+', '')) > 15;
    SELECT RAISE(ABORT, 'phone below E.164 minimum of 7 digits')
    WHERE NEW.phone != '' AND LENGTH(REPLACE(NEW.phone, '+', '')) < 7;
END;
