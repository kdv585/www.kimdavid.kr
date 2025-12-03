package kr.david.gateway.application.usecase;

import kr.david.gateway.domain.entity.ServiceRoute;
import kr.david.gateway.domain.repository.ServiceRouteRepository;
import kr.david.gateway.domain.service.AuthService;
import kr.david.gateway.domain.service.RateLimitService;
import kr.david.gateway.domain.valueobject.RequestContext;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;
import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class ProxyRequestUseCase {
    private final ServiceRouteRepository routeRepository;
    private final AuthService authService;
    private final RateLimitService rateLimitService;
    private final WebClient.Builder webClientBuilder;

    public Mono<ResponseEntity<Object>> execute(
            String path,
            String method,
            Object body,
            RequestContext context
    ) {
        // 라우트 찾기
        Optional<ServiceRoute> routeOpt = routeRepository.findByPath(path);
        if (routeOpt.isEmpty()) {
            return Mono.just(ResponseEntity
                    .status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "Service not found")));
        }

        ServiceRoute route = routeOpt.get();

        // 서비스 상태 확인
        if (route.getStatus() != ServiceRoute.ServiceStatus.ACTIVE) {
            return Mono.just(ResponseEntity
                    .status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Service " + route.getName() + " is " + route.getStatus())));
        }

        // 인증 확인
        if (route.isRequiresAuth()) {
            Optional<String> userId = authService.authenticateRequest(context);
            if (userId.isEmpty()) {
                return Mono.just(ResponseEntity
                        .status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Unauthorized")));
            }
        }

        // 레이트 리미팅 확인
        if (route.getRateLimit() != null) {
            String identifier = context.getUserId() != null 
                    ? context.getUserId() 
                    : context.getIpAddress();
            boolean allowed = rateLimitService.checkRateLimit(
                    identifier, 
                    route.getRateLimit(), 
                    60
            );
            if (!allowed) {
                return Mono.just(ResponseEntity
                        .status(HttpStatus.TOO_MANY_REQUESTS)
                        .body(Map.of("error", "Rate limit exceeded")));
            }
            rateLimitService.incrementCounter(identifier, 60);
        }

        // 프록시 요청
        try {
            WebClient webClient = webClientBuilder
                    .baseUrl(route.getTargetUrl())
                    .build();

            String targetPath = path.replace(route.getPathPrefix(), "");
            String targetUrl = route.getTargetUrl().replaceAll("/$", "") + targetPath;

            WebClient.RequestBodySpec requestSpec = webClient
                    .method(org.springframework.http.HttpMethod.valueOf(method))
                    .uri(targetUrl);

            Mono<ResponseEntity<Object>> response = requestSpec
                    .bodyValue(body != null ? body : "")
                    .retrieve()
                    .toEntity(Object.class)
                    .timeout(Duration.ofSeconds(route.getTimeout()))
                    .onErrorResume(throwable -> {
                        log.error("Proxy error: {}", throwable.getMessage());
                        return Mono.just(ResponseEntity
                                .status(HttpStatus.BAD_GATEWAY)
                                .body(Map.of("error", "Proxy error: " + throwable.getMessage())));
                    });

            return response;
        } catch (Exception e) {
            log.error("Proxy error: {}", e.getMessage());
            return Mono.just(ResponseEntity
                    .status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", "Proxy error: " + e.getMessage())));
        }
    }
}

