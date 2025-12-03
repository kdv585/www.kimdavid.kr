package kr.david.gateway.domain.service;

public interface RateLimitService {
    boolean checkRateLimit(String identifier, int limit, int windowSeconds);
    int incrementCounter(String identifier, int windowSeconds);
}

