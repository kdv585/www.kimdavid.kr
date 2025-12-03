package kr.david.gateway.infrastructure.repository;

import kr.david.gateway.domain.entity.ServiceRoute;
import kr.david.gateway.domain.repository.ServiceRouteRepository;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryServiceRouteRepository implements ServiceRouteRepository {
    private final Map<String, ServiceRoute> routes = new ConcurrentHashMap<>();

    public InMemoryServiceRouteRepository() {
        initializeDefaultRoutes();
    }

    private void initializeDefaultRoutes() {
        ServiceRoute aiServerRoute = ServiceRoute.builder()
                .name("ai-server")
                .pathPrefix("/api/v1/date-courses")
                .targetUrl("http://localhost:8001")
                .status(ServiceRoute.ServiceStatus.ACTIVE)
                .timeout(30)
                .retryCount(3)
                .rateLimit(100)
                .requiresAuth(false)
                .metadata(Map.of("description", "데이트코스 추천 AI 서비스"))
                .build();

        ServiceRoute healthRoute = ServiceRoute.builder()
                .name("health")
                .pathPrefix("/health")
                .targetUrl("http://localhost:8001/health")
                .status(ServiceRoute.ServiceStatus.ACTIVE)
                .timeout(5)
                .retryCount(1)
                .rateLimit(null)
                .requiresAuth(false)
                .metadata(Map.of("description", "헬스 체크"))
                .build();

        routes.put(aiServerRoute.getName(), aiServerRoute);
        routes.put(healthRoute.getName(), healthRoute);
    }

    @Override
    public Optional<ServiceRoute> findByPath(String path) {
        return routes.values().stream()
                .filter(route -> path.startsWith(route.getPathPrefix()))
                .max(Comparator.comparing(route -> route.getPathPrefix().length()));
    }

    @Override
    public Optional<ServiceRoute> findByName(String name) {
        return Optional.ofNullable(routes.get(name));
    }

    @Override
    public List<ServiceRoute> findAll() {
        return new ArrayList<>(routes.values());
    }

    @Override
    public ServiceRoute save(ServiceRoute route) {
        route.validate();
        routes.put(route.getName(), route);
        return route;
    }
}

