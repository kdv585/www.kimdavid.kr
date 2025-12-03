package kr.david.gateway.presentation.controller;

import kr.david.gateway.application.dto.RouteInfoDTO;
import kr.david.gateway.domain.repository.ServiceRouteRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequiredArgsConstructor
public class GatewayController {
    private final ServiceRouteRepository routeRepository;

    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> root() {
        return ResponseEntity.ok(Map.of(
                "message", "API Gateway",
                "version", "1.0.0",
                "status", "running"
        ));
    }

    @GetMapping("/gateway/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "service", "api-gateway"
        ));
    }

    @GetMapping("/gateway/routes")
    public ResponseEntity<List<RouteInfoDTO>> listRoutes() {
        List<RouteInfoDTO> routes = routeRepository.findAll().stream()
                .map(route -> RouteInfoDTO.builder()
                        .name(route.getName())
                        .pathPrefix(route.getPathPrefix())
                        .targetUrl(route.getTargetUrl())
                        .status(route.getStatus().name())
                        .requiresAuth(route.isRequiresAuth())
                        .rateLimit(route.getRateLimit())
                        .build())
                .collect(Collectors.toList());

        return ResponseEntity.ok(routes);
    }
}

