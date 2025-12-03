package kr.david.gateway.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OAuthUserDTO {
    private String id;
    private String email;
    private String name;
    private String nickname;
    private String provider; // kakao, naver, google
    private String profileImage;
}

