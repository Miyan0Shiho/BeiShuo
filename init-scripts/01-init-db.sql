-- 碑说项目数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建碑文表
CREATE TABLE IF NOT EXISTS inscriptions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    dynasty VARCHAR(50),
    location VARCHAR(200),
    author VARCHAR(100),
    created_year VARCHAR(50),
    image_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建知识库表
CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    dynasty VARCHAR(50),
    tags TEXT,
    source VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建对话表
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    inscription_id INTEGER REFERENCES inscriptions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_inscriptions_dynasty ON inscriptions(dynasty);
CREATE INDEX IF NOT EXISTS idx_inscriptions_status ON inscriptions(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_dynasty ON knowledge(dynasty);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 插入测试数据
INSERT INTO users (username, email, password_hash, display_name, role) VALUES
('testuser', 'test@beishuo.com', '$2a$10$examplehash', '测试用户', 'user'),
('admin', 'admin@beishuo.com', '$2a$10$adminhash', '管理员', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入示例碑文数据
INSERT INTO inscriptions (title, content, dynasty, location, author, created_year) VALUES
('唐代碑文示例', '大唐盛世，文化繁荣，此碑记载了当时的辉煌历史...', '唐', '陕西西安', '无名氏', '公元750年'),
('宋代石刻', '宋代文化发达，石刻艺术达到高峰...', '宋', '河南洛阳', '苏轼', '公元1100年')
ON CONFLICT DO NOTHING;

-- 插入示例知识库数据
INSERT INTO knowledge (title, content, category, dynasty, tags) VALUES
('碑文发展历史', '碑文作为中国古代文化的重要载体，经历了漫长的发展历程...', '历史', '历代', '碑文,历史,文化'),
('石刻艺术特点', '中国古代石刻艺术具有独特的审美价值和技术特点...', '艺术', '历代', '石刻,艺术,技术')
ON CONFLICT DO NOTHING;