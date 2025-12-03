package kr.david.gateway.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RouteInfoDTO {
    private String name;
    private String pathPrefix;
    private String targetUrl;
    private String status;
    private boolean requiresAuth;
    private Integer rateLimit;
}

