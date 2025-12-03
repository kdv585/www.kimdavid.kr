package kr.david.gateway.presentation.controller;

import kr.david.gateway.infrastructure.service.OAuthService;
import kr.david.gateway.infrastructure.service.JwtAuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class OAuthController {
    private final OAuthService oAuthService;
    private final JwtAuthService jwtAuthService;

    @Value("${KAKAO_REDIRECT_URI:http://localhost:8000/api/auth/kakao/callback}")
    private String kakaoRedirectUri;

    @Value("${NAVER_REDIRECT_URI:http://localhost:8000/api/auth/naver/callback}")
    private String naverRedirectUri;

    @Value("${GOOGLE_REDIRECT_URI:http://localhost:8000/api/auth/google/callback}")
    private String googleRedirectUri;

    @Value("${KAKAO_CLIENT_ID:}")
    private String kakaoClientId;

    @Value("${NAVER_CLIENT_ID:}")
    private String naverClientId;

    @Value("${GOOGLE_CLIENT_ID:}")
    private String googleClientId;

    @GetMapping("/kakao")
    public ResponseEntity<Map<String, String>> kakaoLogin() {
        if (kakaoClientId.isEmpty()) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Kakao Client ID가 설정되지 않았습니다."));
        }
        
        String authUrl = "https://kauth.kakao.com/oauth/authorize" +
                "?client_id=" + kakaoClientId +
                "&redirect_uri=" + kakaoRedirectUri +
                "&response_type=code";
        
        return ResponseEntity.ok(Map.of("authUrl", authUrl));
    }

    @GetMapping("/kakao/callback")
    public Mono<ResponseEntity<Map<String, Object>>> kakaoCallback(@RequestParam String code) {
        return oAuthService.getKakaoToken(code, kakaoRedirectUri)
                .flatMap(token -> oAuthService.getKakaoUser(token.getAccessToken()))
                .map(user -> {
                    // JWT 토큰 생성 (실제 구현 필요)
                    String jwtToken = jwtAuthService.generateToken(user.getId());
                    
                    return ResponseEntity.ok(Map.of(
                            "user", user,
                            "token", jwtToken,
                            "message", "Kakao 로그인 성공"
                    ));
                })
                .onErrorResume(error -> {
                    log.error("Kakao OAuth error: {}", error.getMessage());
                    return Mono.just(ResponseEntity
                            .status(HttpStatus.INTERNAL_SERVER_ERROR)
                            .body(Map.of("error", "Kakao 로그인 실패: " + error.getMessage())));
                });
    }

    @GetMapping("/naver")
    public ResponseEntity<Map<String, String>> naverLogin() {
        if (naverClientId.isEmpty()) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Naver Client ID가 설정되지 않았습니다."));
        }
        
        String authUrl = "https://nid.naver.com/oauth2.0/authorize" +
                "?client_id=" + naverClientId +
                "&redirect_uri=" + naverRedirectUri +
                "&response_type=code" +
                "&state=STATE_STRING";
        
        return ResponseEntity.ok(Map.of("authUrl", authUrl));
    }

    @GetMapping("/naver/callback")
    public Mono<ResponseEntity<Map<String, Object>>> naverCallback(@RequestParam String code) {
        return oAuthService.getNaverToken(code, naverRedirectUri)
                .flatMap(token -> oAuthService.getNaverUser(token.getAccessToken()))
                .map(user -> {
                    String jwtToken = jwtAuthService.generateToken(user.getId());
                    
                    return ResponseEntity.ok(Map.of(
                            "user", user,
                            "token", jwtToken,
                            "message", "Naver 로그인 성공"
                    ));
                })
                .onErrorResume(error -> {
                    log.error("Naver OAuth error: {}", error.getMessage());
                    return Mono.just(ResponseEntity
                            .status(HttpStatus.INTERNAL_SERVER_ERROR)
                            .body(Map.of("error", "Naver 로그인 실패: " + error.getMessage())));
                });
    }

    @GetMapping("/google")
    public ResponseEntity<Map<String, String>> googleLogin() {
        if (googleClientId.isEmpty()) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Google Client ID가 설정되지 않았습니다."));
        }
        
        String authUrl = "https://accounts.google.com/o/oauth2/v2/auth" +
                "?client_id=" + googleClientId +
                "&redirect_uri=" + googleRedirectUri +
                "&response_type=code" +
                "&scope=profile email";
        
        return ResponseEntity.ok(Map.of("authUrl", authUrl));
    }

    @GetMapping("/google/callback")
    public Mono<ResponseEntity<Map<String, Object>>> googleCallback(@RequestParam String code) {
        return oAuthService.getGoogleToken(code, googleRedirectUri)
                .flatMap(token -> oAuthService.getGoogleUser(token.getAccessToken()))
                .map(user -> {
                    String jwtToken = jwtAuthService.generateToken(user.getId());
                    
                    return ResponseEntity.ok(Map.of(
                            "user", user,
                            "token", jwtToken,
                            "message", "Google 로그인 성공"
                    ));
                })
                .onErrorResume(error -> {
                    log.error("Google OAuth error: {}", error.getMessage());
                    return Mono.just(ResponseEntity
                            .status(HttpStatus.INTERNAL_SERVER_ERROR)
                            .body(Map.of("error", "Google 로그인 실패: " + error.getMessage())));
                });
    }
}

