package kr.david.gateway.infrastructure.service;

import kr.david.gateway.application.dto.OAuthTokenDTO;
import kr.david.gateway.application.dto.OAuthUserDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class OAuthService {
    private final WebClient.Builder webClientBuilder;

    @Value("${KAKAO_CLIENT_ID:}")
    private String kakaoClientId;

    @Value("${KAKAO_CLIENT_SECRET:}")
    private String kakaoClientSecret;

    @Value("${NAVER_CLIENT_ID:}")
    private String naverClientId;

    @Value("${NAVER_CLIENT_SECRET:}")
    private String naverClientSecret;

    @Value("${GOOGLE_CLIENT_ID:}")
    private String googleClientId;

    @Value("${GOOGLE_CLIENT_SECRET:}")
    private String googleClientSecret;

    public Mono<OAuthTokenDTO> getKakaoToken(String code, String redirectUri) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.post()
                .uri("https://kauth.kakao.com/oauth/token")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(BodyInserters.fromFormData("grant_type", "authorization_code")
                        .with("client_id", kakaoClientId)
                        .with("client_secret", kakaoClientSecret)
                        .with("redirect_uri", redirectUri)
                        .with("code", code))
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> OAuthTokenDTO.builder()
                        .accessToken((String) response.get("access_token"))
                        .tokenType((String) response.get("token_type"))
                        .refreshToken((String) response.get("refresh_token"))
                        .expiresIn(((Number) response.get("expires_in")).longValue())
                        .scope((String) response.get("scope"))
                        .build())
                .doOnError(error -> log.error("Kakao token error: {}", error.getMessage()));
    }

    public Mono<OAuthUserDTO> getKakaoUser(String accessToken) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.get()
                .uri("https://kapi.kakao.com/v2/user/me")
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> kakaoAccount = (Map<String, Object>) response.get("kakao_account");
                    @SuppressWarnings("unchecked")
                    Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
                    
                    return OAuthUserDTO.builder()
                            .id(String.valueOf(response.get("id")))
                            .email((String) kakaoAccount.get("email"))
                            .nickname((String) profile.get("nickname"))
                            .profileImage((String) profile.get("profile_image_url"))
                            .provider("kakao")
                            .build();
                })
                .doOnError(error -> log.error("Kakao user info error: {}", error.getMessage()));
    }

    public Mono<OAuthTokenDTO> getNaverToken(String code, String redirectUri) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.post()
                .uri("https://nid.naver.com/oauth2.0/token")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(BodyInserters.fromFormData("grant_type", "authorization_code")
                        .with("client_id", naverClientId)
                        .with("client_secret", naverClientSecret)
                        .with("redirect_uri", redirectUri)
                        .with("code", code))
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> OAuthTokenDTO.builder()
                        .accessToken((String) response.get("access_token"))
                        .tokenType((String) response.get("token_type"))
                        .refreshToken((String) response.get("refresh_token"))
                        .expiresIn(((Number) response.get("expires_in")).longValue())
                        .scope((String) response.get("scope"))
                        .build())
                .doOnError(error -> log.error("Naver token error: {}", error.getMessage()));
    }

    public Mono<OAuthUserDTO> getNaverUser(String accessToken) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.get()
                .uri("https://openapi.naver.com/v1/nid/me")
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> responseData = (Map<String, Object>) response.get("response");
                    
                    return OAuthUserDTO.builder()
                            .id((String) responseData.get("id"))
                            .email((String) responseData.get("email"))
                            .name((String) responseData.get("name"))
                            .nickname((String) responseData.get("nickname"))
                            .profileImage((String) responseData.get("profile_image"))
                            .provider("naver")
                            .build();
                })
                .doOnError(error -> log.error("Naver user info error: {}", error.getMessage()));
    }

    public Mono<OAuthTokenDTO> getGoogleToken(String code, String redirectUri) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.post()
                .uri("https://oauth2.googleapis.com/token")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(BodyInserters.fromFormData("grant_type", "authorization_code")
                        .with("client_id", googleClientId)
                        .with("client_secret", googleClientSecret)
                        .with("redirect_uri", redirectUri)
                        .with("code", code))
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> OAuthTokenDTO.builder()
                        .accessToken((String) response.get("access_token"))
                        .tokenType((String) response.get("token_type"))
                        .refreshToken((String) response.get("refresh_token"))
                        .expiresIn(((Number) response.get("expires_in")).longValue())
                        .scope((String) response.get("scope"))
                        .build())
                .doOnError(error -> log.error("Google token error: {}", error.getMessage()));
    }

    public Mono<OAuthUserDTO> getGoogleUser(String accessToken) {
        WebClient webClient = webClientBuilder.build();
        
        return webClient.get()
                .uri("https://www.googleapis.com/oauth2/v2/userinfo")
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> OAuthUserDTO.builder()
                        .id((String) response.get("id"))
                        .email((String) response.get("email"))
                        .name((String) response.get("name"))
                        .profileImage((String) response.get("picture"))
                        .provider("google")
                        .build())
                .doOnError(error -> log.error("Google user info error: {}", error.getMessage()));
    }
}

