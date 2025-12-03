package kr.david.gateway.infrastructure.service;

import kr.david.gateway.domain.service.RateLimitService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@ConditionalOnMissingBean(RedisRateLimitService.class)
public class InMemoryRateLimitService implements RateLimitService {
    private final Map<String, Integer> counters = new ConcurrentHashMap<>();
    private final Map<String, Long> timestamps = new ConcurrentHashMap<>();

    @Override
    public boolean checkRateLimit(String identifier, int limit, int windowSeconds) {
        String key = getKey(identifier, windowSeconds);
        int count = counters.getOrDefault(key, 0);
        return count < limit;
    }

    @Override
    public int incrementCounter(String identifier, int windowSeconds) {
        String key = getKey(identifier, windowSeconds);
        int count = counters.getOrDefault(key, 0);
        counters.put(key, count + 1);
        timestamps.put(key, System.currentTimeMillis());

        // 오래된 키 정리
        cleanupOldKeys(windowSeconds);

        return counters.get(key);
    }

    private String getKey(String identifier, int windowSeconds) {
        long currentWindow = System.currentTimeMillis() / (windowSeconds * 1000L);
        return identifier + ":" + currentWindow;
    }

    private void cleanupOldKeys(int windowSeconds) {
        long currentTime = System.currentTimeMillis();
        timestamps.entrySet().removeIf(entry -> {
            if (currentTime - entry.getValue() > windowSeconds * 2000L) {
                counters.remove(entry.getKey());
                return true;
            }
            return false;
        });
    }
}

