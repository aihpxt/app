# 前端服务启动指南

## 问题描述
前端服务不可用，访问 http://localhost:3000/#/ 时显示服务不可用。

## 解决方案

### 方法一：使用Vite开发服务器
1. 打开命令行终端
2. 导航到前端项目目录：`cd e:\aiphxt-app\frontend`
3. 安装依赖项：`npm install`
4. 启动开发服务器：`npm run dev`
5. 访问 http://localhost:3000/#/ 查看前端服务

### 方法二：使用Python内置HTTP服务器
1. 打开命令行终端
2. 导航到前端项目目录：`cd e:\aiphxt-app\frontend`
3. 启动HTTP服务器：`python -m http.server 3000`
4. 访问 http://localhost:3000/#/ 查看前端服务

## 注意事项
- 确保系统中已经安装了Node.js和npm
- 确保系统中已经安装了Python
- 确保端口3000没有被其他程序占用
- 如果遇到依赖项安装失败的问题，可以尝试删除node_modules目录后重新安装依赖项
