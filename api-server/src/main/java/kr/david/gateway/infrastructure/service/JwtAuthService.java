package kr.david.gateway.infrastructure.service;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.security.Keys;
import kr.david.gateway.domain.service.AuthService;
import kr.david.gateway.domain.valueobject.RequestContext;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import io.jsonwebtoken.Jwts;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.Optional;

@Slf4j
@Service
public class JwtAuthService implements AuthService {
    private final SecretKey secretKey;

    public JwtAuthService(@Value("${jwt.secret:your-secret-key-change-in-production}") String secret) {
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public Optional<String> verifyToken(String token) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
            return Optional.ofNullable(claims.getSubject());
        } catch (Exception e) {
            log.warn("Token verification failed: {}", e.getMessage());
            return Optional.empty();
        }
    }

    @Override
    public Optional<String> authenticateRequest(RequestContext context) {
        String authHeader = context.getHeaders().getOrDefault("authorization", "");
        if (!authHeader.startsWith("Bearer ")) {
            return Optional.empty();
        }

        String token = authHeader.substring(7);
        return verifyToken(token);
    }

    public String generateToken(String userId) {
        Instant now = Instant.now();
        Instant expiry = now.plus(7, ChronoUnit.DAYS);

        return Jwts.builder()
                .subject(userId)
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiry))
                .signWith(secretKey)
                .compact();
    }
}

