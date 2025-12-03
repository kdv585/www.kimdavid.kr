package kr.david.gateway.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OAuthTokenDTO {
    private String accessToken;
    private String tokenType;
    private String refreshToken;
    private Long expiresIn;
    private String scope;
}

