package kr.david.gateway.domain.service;

import kr.david.gateway.domain.valueobject.RequestContext;

import java.util.Optional;

public interface AuthService {
    Optional<String> verifyToken(String token);
    Optional<String> authenticateRequest(RequestContext context);
}

