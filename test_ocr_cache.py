import hashlib

# 计算文件的MD5哈希值
file_path = '/Users/liuminxuan/Desktop/团队项目/vertical_1.png'
with open(file_path, 'rb') as f:
    content = f.read()
    md5_hash = hashlib.md5(content).hexdigest()
    
print(f"文件: {file_path}")
print(f"MD5哈希值: {md5_hash}")
print(f"文件大小: {len(content)} bytes")