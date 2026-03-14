# 前端Dockerfile - 构建阶段
FROM node:20-slim AS builder

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY package.json package-lock.json* /app/

# 安装依赖
RUN npm install

# 复制源代码
COPY . /app/

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]