package kr.david.gateway.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.Map;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ServiceRoute {
    private String name;
    private String pathPrefix;
    private String targetUrl;
    private ServiceStatus status;
    private int timeout; // 초 단위
    private int retryCount;
    private Integer rateLimit; // 분당 요청 수
    private boolean requiresAuth;
    private Map<String, Object> metadata;

    public enum ServiceStatus {
        ACTIVE, INACTIVE, MAINTENANCE
    }

    public void validate() {
        if (timeout <= 0) {
            throw new IllegalArgumentException("타임아웃은 0보다 커야 합니다.");
        }
        if (retryCount < 0) {
            throw new IllegalArgumentException("재시도 횟수는 0 이상이어야 합니다.");
        }
    }
}

