CREATE TABLE IF NOT EXISTS fbuser (
  u_id INTEGER PRIMARY KEY AUTOINCREMENT, u_created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  u_uid TEXT NOT NULL UNIQUE, u_email TEXT NOT NULL UNIQUE, u_name TEXT, u_photo TEXT, u_password_hash TEXT, u_is_admin INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS content (
  c_id INTEGER PRIMARY KEY AUTOINCREMENT, c_created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  c_title TEXT NOT NULL, c_text TEXT, c_status TEXT CHECK (c_status IN ('on','off','del')) DEFAULT 'on',
  c_owner INTEGER, FOREIGN KEY (c_owner) REFERENCES fbuser(u_id)
);
CREATE TABLE IF NOT EXISTS contact (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, name TEXT, email TEXT,
  subject TEXT, message TEXT, status TEXT CHECK (status IN ('recebido','lido','respondido','apagado')) DEFAULT 'recebido'
);
INSERT OR IGNORE INTO fbuser (u_uid,u_email,u_name) VALUES
  ('qwertyuiop','joca@silva.com','Joca da Silva'), ('asdfghjkl','mairneuza@siri.com','Marineuza Siriliano');
INSERT INTO content (c_title,c_text,c_owner)
SELECT 'Como fazer pipoca na praia','Lorem ipsum dolor sit amet consectetur adipisicing elit.',1
WHERE NOT EXISTS (SELECT 1 FROM content);
