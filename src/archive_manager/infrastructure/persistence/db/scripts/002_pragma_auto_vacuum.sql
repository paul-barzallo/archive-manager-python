-- Configuration: Enable incremental auto-vacuum
-- Purpose: Automatic space reclamation when data is deleted
-- Note: This is a persistent database setting

PRAGMA auto_vacuum = INCREMENTAL;
