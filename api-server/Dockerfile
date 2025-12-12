FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /app

# Maven 의존성 다운로드 (캐시 활용)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 소스 코드 복사 및 빌드
COPY src ./src
RUN mvn clean package -DskipTests

# 실행 이미지
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 빌드된 JAR 파일 복사
COPY --from=build /app/target/*.jar app.jar

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행 (포트 8080으로 명시적 설정)
ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=8080"]

