package kr.david.gateway.presentation.filter;

import kr.david.gateway.domain.valueobject.RequestContext;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Component
public class RequestContextFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 요청 컨텍스트 생성
        Map<String, String> headers = new HashMap<>();
        request.getHeaders().forEach((key, values) -> {
            if (!values.isEmpty()) {
                headers.put(key.toLowerCase(), values.get(0));
            }
        });

        RequestContext context = RequestContext.builder()
                .requestId(UUID.randomUUID().toString())
                .ipAddress(request.getRemoteAddress() != null 
                        ? request.getRemoteAddress().getAddress().getHostAddress() 
                        : "")
                .userAgent(headers.getOrDefault("user-agent", ""))
                .timestamp(LocalDateTime.now())
                .headers(headers)
                .build();

        // 요청에 컨텍스트 저장
        exchange.getAttributes().put("requestContext", context);

        // 응답 헤더에 요청 ID 추가
        exchange.getResponse().getHeaders().add("X-Request-ID", context.getRequestId());

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return -100;
    }
}

