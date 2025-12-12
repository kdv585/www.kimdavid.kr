package kr.david.gateway.presentation.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Slf4j
@Component
public class LoggingFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        long startTime = System.currentTimeMillis();

        log.info("Request: {} {} - IP: {}",
                request.getMethod(),
                request.getURI().getPath(),
                request.getRemoteAddress());

        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            ServerHttpResponse response = exchange.getResponse();
            long duration = System.currentTimeMillis() - startTime;

            log.info("Response: {} {} - Status: {} - Time: {}ms",
                    request.getMethod(),
                    request.getURI().getPath(),
                    response.getStatusCode(),
                    duration);

            // 응답이 커밋되기 전에만 헤더 추가 가능
            if (!response.isCommitted()) {
                try {
                    response.getHeaders().add("X-Process-Time", String.valueOf(duration));
                } catch (UnsupportedOperationException e) {
                    // 읽기 전용 헤더인 경우 무시
                    log.debug("Cannot add header to committed response: {}", e.getMessage());
                }
            }
        }));
    }

    @Override
    public int getOrder() {
        return -50;
    }
}
