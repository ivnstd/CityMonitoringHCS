CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    local_id INTEGER NOT NULL,
    source VARCHAR(10) NOT NULL,
    date TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    from_user VARCHAR(255) NOT NULL,
    text TEXT,
    image BYTEA,
	problem TEXT,
    address TEXT,
    coordinates TEXT
);