# ─────────────────────────────────────────────────────────────
#  Stage 1 – Build JAR bằng Maven
# ─────────────────────────────────────────────────────────────
FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

# Copy pom.xml trước để tận dụng Docker layer cache (dependencies)
COPY pom.xml .
RUN mvn dependency:go-offline -q

# Copy source rồi build
COPY src ./src
RUN mvn package -DskipTests -q

# ─────────────────────────────────────────────────────────────
#  Stage 2 – Runtime image nhỏ gọn
# ─────────────────────────────────────────────────────────────
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy JAR từ stage build
COPY --from=builder /app/target/*.jar app.jar

# Port backend
EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
