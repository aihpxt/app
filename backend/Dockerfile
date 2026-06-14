# 基础镜像
FROM openjdk:17-jdk-alpine

# 设置工作目录
WORKDIR /app

# 复制构建好的jar包
COPY target/school-platform-backend-1.0.0.jar app.jar

# 暴露端口
EXPOSE 8080

# 启动服务
CMD ["java", "-jar", "app.jar"]