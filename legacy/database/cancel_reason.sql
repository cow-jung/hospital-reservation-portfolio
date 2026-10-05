ALTER TABLE reservations
ADD COLUMN cancel_reason VARCHAR(255) NULL;

DESCRIBE reservations;