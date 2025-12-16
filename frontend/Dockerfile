# 前端Dockerfile
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

<<<<<<< HEAD
# 暴露端口
EXPOSE 5173

# 启动命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
=======
FROM node:20-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY package.json package-lock.json ./
RUN npm ci
EXPOSE 5173
CMD ["npm","run","preview","--","--host","0.0.0.0","--port","5173"]
>>>>>>> hebin
