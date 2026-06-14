# 基础镜像
FROM node:16-alpine

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json ./

# 安装依赖
RUN npm install

# 复制代码
COPY . .

# 构建项目
RUN npm run build

# 安装静态文件服务器
RUN npm install -g serve

# 暴露端口
EXPOSE 3000

# 启动服务
CMD ["serve", "-s", "dist", "-l", "3000"]