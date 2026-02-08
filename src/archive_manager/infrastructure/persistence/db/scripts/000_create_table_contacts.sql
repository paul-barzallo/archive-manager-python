-- Table: contacts
-- Core table for contact management with soft delete support

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(16) NOT NULL DEFAULT '',  -- E.164: '+' + max 15 digits
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    deleted_at DATETIME DEFAULT NULL
);

-- Unique email for non-deleted contacts
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_email_unique
ON contacts(email) WHERE deleted_at IS NULL;

-- Unique phone for non-deleted contacts (when phone is not empty)
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_phone_unique
ON contacts(phone) WHERE deleted_at IS NULL AND phone != '';

-- Index for first name searches
CREATE INDEX IF NOT EXISTS idx_contacts_first_name
ON contacts(first_name);

-- Index for last name searches
CREATE INDEX IF NOT EXISTS idx_contacts_last_name
ON contacts(last_name);

-- Composite index for full name searches
CREATE INDEX IF NOT EXISTS idx_contacts_full_name
ON contacts(first_name, last_name);

-- Index for listing active contacts (filtering by deleted_at)
CREATE INDEX IF NOT EXISTS idx_contacts_active
ON contacts(deleted_at);
