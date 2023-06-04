CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY unique,
  telegram_id int NOT NULL,
  username text NOT NULL,
  password text NOT NULL,
  number_of_files int
);
CREATE TABLE IF NOT EXISTS file (
  id SERIAL PRIMARY KEY,
  name text NOT NULL,
  owner_user_id int NOT NULL,
  owner_telegram_id int NOT NULL,
  content bytea NOT NULL,
  size int NOT NULL,
  created_at timestamp
);
ALTER TABLE file ADD FOREIGN KEY (owner_user_id) REFERENCES users (id);