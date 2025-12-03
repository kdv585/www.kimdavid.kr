package kr.david.gateway.domain.repository;

import kr.david.gateway.domain.entity.ServiceRoute;

import java.util.List;
import java.util.Optional;

public interface ServiceRouteRepository {
    Optional<ServiceRoute> findByPath(String path);
    Optional<ServiceRoute> findByName(String name);
    List<ServiceRoute> findAll();
    ServiceRoute save(ServiceRoute route);
}

