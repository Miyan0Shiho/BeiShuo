# ==========================
FROM maven:3.9.6-eclipse-temurin-17 AS builder
WORKDIR /workspace

# 配置Maven镜像源
RUN echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > /usr/share/maven/conf/settings.xml \
    && echo "<settings xmlns=\"http://maven.apache.org/SETTINGS/1.0.0\"" >> /usr/share/maven/conf/settings.xml \
    && echo "          xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"" >> /usr/share/maven/conf/settings.xml \
    && echo "          xsi:schemaLocation=\"http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd\">" >> /usr/share/maven/conf/settings.xml \
    && echo "    <mirrors>" >> /usr/share/maven/conf/settings.xml \
    && echo "        <mirror>" >> /usr/share/maven/conf/settings.xml \
    && echo "            <id>aliyunmaven</id>" >> /usr/share/maven/conf/settings.xml \
    && echo "            <mirrorOf>*</mirrorOf>" >> /usr/share/maven/conf/settings.xml \
    && echo "            <name>阿里云公共仓库</name>" >> /usr/share/maven/conf/settings.xml \
    && echo "            <url>https://maven.aliyun.com/repository/public</url>" >> /usr/share/maven/conf/settings.xml \
    && echo "        </mirror>" >> /usr/share/maven/conf/settings.xml \
    && echo "    </mirrors>" >> /usr/share/maven/conf/settings.xml \
    && echo "</settings>" >> /usr/share/maven/conf/settings.xml

COPY pom.xml .
COPY src ./src
RUN mvn -B -DskipTests package

# ==========================
FROM openjdk:17-jre-slim
WORKDIR /app
ENV JAVA_OPTS=""
COPY --from=builder /workspace/target/*.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar /app/app.jar"]