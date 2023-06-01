CREATE TABLE IF NOT EXISTS "users" (
  "id" SERIAL PRIMARY KEY,
  "username" text NOT NULL UNIQUE,
  "password" text NOT NULL,
  "number_of_files" int
);
CREATE TABLE IF NOT EXISTS "file" (
  "id" SERIAL PRIMARY KEY,
  "name" text NOT NULL,
  "user_id" int NOT NULL,
  "size" int NOT NULL,
  "created_at" timestamp
);
ALTER TABLE "file" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");