CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    language VARCHAR(2) DEFAULT 'ru',
    notify_time TIME DEFAULT '09:00',
    notify_period_days INT DEFAULT 7,
    timezone VARCHAR(50) DEFAULT 'Europe/Vienna',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calendar (
    cal_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    text TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME,
    status SMALLINT DEFAULT 0,
    is_urgent BOOLEAN DEFAULT FALSE,
    repeat BOOLEAN DEFAULT FALSE,
    repeat_every_days INT,
    next_run_date DATE,
    notify_before_hours INT DEFAULT 24,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE folders (
    folder_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    folder_name VARCHAR(255) NOT NULL,
    parent_folder_id INT REFERENCES folders(folder_id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    tg_file_id VARCHAR(255) NOT NULL,
    file_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE knowledge (
    knowledge_id SERIAL PRIMARY KEY,
    folder_id INT REFERENCES folders(folder_id),
    file_id INT REFERENCES files(file_id),
    text TEXT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);