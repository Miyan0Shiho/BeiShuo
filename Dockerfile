# ==========================
FROM maven:3.9.6-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY pom.xml .
COPY src ./src
RUN mvn -B -DskipTests package

# ==========================
FROM eclipse-temurin:17-jre
WORKDIR /app
ENV JAVA_OPTS=""
COPY --from=builder /workspace/target/*.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar /app/app.jar"]