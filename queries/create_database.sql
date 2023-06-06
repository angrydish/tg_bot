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

CREATE OR REPLACE FUNCTION update_file_count()
RETURNS TRIGGER AS $$
DECLARE
  user_id INT;
BEGIN
  IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
    user_id := NEW.owner_user_id;
  ELSE
    user_id := OLD.owner_user_id;
  END IF;
  UPDATE users SET number_of_files = (SELECT COUNT(*) FROM file WHERE owner_user_id = user_id) WHERE id = user_id;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_file_count
AFTER INSERT OR UPDATE OR DELETE ON file
FOR EACH ROW
EXECUTE PROCEDURE update_file_count();