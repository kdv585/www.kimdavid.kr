package kr.david.gateway.infrastructure.service;

import kr.david.gateway.domain.service.RateLimitService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Slf4j
@Service
@RequiredArgsConstructor
public class RedisRateLimitService implements RateLimitService {
    private final RedisTemplate<String, String> redisTemplate;

    @Override
    public boolean checkRateLimit(String identifier, int limit, int windowSeconds) {
        String key = getKey(identifier, windowSeconds);
        String countStr = redisTemplate.opsForValue().get(key);
        
        if (countStr == null) {
            return true;
        }
        
        int count = Integer.parseInt(countStr);
        return count < limit;
    }

    @Override
    public int incrementCounter(String identifier, int windowSeconds) {
        String key = getKey(identifier, windowSeconds);
        Long count = redisTemplate.opsForValue().increment(key);
        
        if (count == 1) {
            redisTemplate.expire(key, windowSeconds, TimeUnit.SECONDS);
        }
        
        return count != null ? count.intValue() : 0;
    }

    private String getKey(String identifier, int windowSeconds) {
        long currentWindow = System.currentTimeMillis() / (windowSeconds * 1000L);
        return "rate_limit:" + identifier + ":" + currentWindow;
    }
}

