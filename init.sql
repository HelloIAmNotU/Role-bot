CREATE TABLE messages (
    guild_id BIGINT PRIMARY KEY,
    message_id BIGINT,
    message_content TEXT,
    emojis TEXT ARRAY,
    role_ids BIGINT ARRAY
);