package kr.david.gateway.domain.valueobject;

import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.Map;

@Getter
@Builder
public class RequestContext {
    private final String requestId;
    private final String userId;
    private final String ipAddress;
    private final String userAgent;
    private final LocalDateTime timestamp;
    private final Map<String, String> headers;
    private final Map<String, Object> metadata;
}

