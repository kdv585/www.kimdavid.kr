import sys
from pathlib import Path
import pandas as pd
import numpy as np
import importlib.util

try:
    import folium
    from folium.plugins import HeatMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Import 경로 설정 (Docker/로컬 환경 모두 지원)
current_file = Path(__file__).resolve()
if str(current_file).startswith("/app"):
    # Docker 환경 - 실제 경로를 우선 시도 (볼륨 마운트로 인해 /app/app/seoul_crime 구조)
    try:
        from app.seoul_crime.seoul_method import SeoulMethod
        from app.seoul_crime.seoul_data import SeoulData
        from app.seoul_crime.kakao_map_singleton import KakaoMapSingleton
        # common.utils를 직접 로드
        try:
            from app.common.utils import setup_logging
        except ImportError:
            utils_path = Path("/app/common/utils.py")
            if utils_path.exists():
                spec = importlib.util.spec_from_file_location("common_utils", str(utils_path))
                common_utils = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(common_utils)
                setup_logging = common_utils.setup_logging
            else:
                raise ImportError("common/utils.py를 찾을 수 없습니다")
    except ImportError:
        try:
            from app.ml_service.app.seoul_crime.seoul_method import SeoulMethod
            from app.ml_service.app.seoul_crime.seoul_data import SeoulData
            from app.ml_service.app.seoul_crime.kakao_map_singleton import KakaoMapSingleton
            from app.ml_service.common.utils import setup_logging
        except ImportError as e:
            raise ImportError(f"모든 import 경로 실패: {e}")
else:
    # 로컬 환경
    from app.ml_service.app.seoul_crime.seoul_method import SeoulMethod
    from app.ml_service.app.seoul_crime.seoul_data import SeoulData
    from app.ml_service.app.seoul_crime.kakao_map_singleton import KakaoMapSingleton
    from app.ml_service.common.utils import setup_logging

try:
    logger = setup_logging("seoul_service")
except (ImportError, NameError):
    import logging
    logger = logging.getLogger("seoul_service")
class SeoulService:
    
    def __init__(self):
        self.data = SeoulData()
        self.method = SeoulMethod()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']

    def load_data(self):
        """데이터를 로드하고 merge된 데이터 및 지도 정보를 반환"""
        try:
            data_dir = Path(self.data.dname)
            cctv_path = data_dir / "cctv.csv"
            crime_path = data_dir / "crime.csv"
            pop_path = data_dir / "pop.csv"

            logger.info(f"데이터 로드 시작: {data_dir}")
            
            # 데이터 로드
            cctv = self.method.csv_to_df(str(cctv_path))
            
            # crime.csv 헤더 읽기 (3행과 4행을 조합하여 컬럼명 생성)
            crime_header_row3 = pd.read_csv(str(crime_path), skiprows=2, nrows=1, header=None, encoding='utf-8')
            crime_header_row4 = pd.read_csv(str(crime_path), skiprows=3, nrows=1, header=None, encoding='utf-8')
            
            # 컬럼명 생성: 3행과 4행을 조합 (예: "소계_발생", "살인_검거" 등)
            column_names = ['무시', '자치구']  # 첫 두 컬럼은 고정
            for i in range(2, len(crime_header_row3.columns)):
                row3_val = str(crime_header_row3.iloc[0, i]).strip() if i < len(crime_header_row3.columns) else ""
                row4_val = str(crime_header_row4.iloc[0, i]).strip() if i < len(crime_header_row4.columns) else ""
                if row3_val and row4_val:
                    column_names.append(f"{row3_val}_{row4_val}")
                elif row3_val:
                    column_names.append(row3_val)
                elif row4_val:
                    column_names.append(row4_val)
                else:
                    column_names.append(f'col_{i}')
            
            # crime.csv는 첫 4행이 헤더이므로 skiprows=4 사용
            crime = pd.read_csv(str(crime_path), skiprows=4, header=None, encoding='utf-8')
            # 컬럼명 설정
            if len(crime.columns) >= 2:
                # 컬럼 수에 맞게 조정
                final_column_names = column_names[:len(crime.columns)]
                if len(final_column_names) < len(crime.columns):
                    final_column_names += [f'col_{i}' for i in range(len(final_column_names), len(crime.columns))]
                crime.columns = final_column_names
                # 첫 번째 행("합계", "소계") 제거
                if len(crime) > 0 and str(crime.iloc[0, 0]) == "합계":
                    crime = crime.drop(crime.index[0])
            else:
                raise ValueError(f"crime 데이터 컬럼 수가 부족합니다: {len(crime.columns)}")
            
            logger.info(f"crime 컬럼: {crime.columns.tolist()}")
            logger.info(f"crime 첫 5행:\n{crime.head()}")
            
            # pop.csv는 첫 3행이 헤더이므로 skiprows=3 사용하고 컬럼명 직접 지정
            # 실제 데이터는 4행부터 시작하며, 두 번째 컬럼이 자치구, 네 번째 컬럼이 인구수
            pop = pd.read_csv(str(pop_path), skiprows=3, header=None, encoding='utf-8')
            
            logger.info(f"데이터 로드 완료: cctv={cctv.shape}, crime={crime.shape}, pop={pop.shape}")
            logger.info(f"cctv 컬럼: {cctv.columns.tolist()}")
            logger.info(f"pop 원본 컬럼 수: {len(pop.columns)}")
            logger.info(f"pop 첫 5행:\n{pop.head()}")
            
            # 컬럼명 설정: 첫 번째 컬럼은 무시, 두 번째가 자치구, 네 번째가 인구수
            if len(pop.columns) >= 4:
                pop.columns = ['무시', '자치구', '무시2', '인구수'] + [f'col_{i}' for i in range(4, len(pop.columns))]
                pop = pop[['자치구', '인구수']]  # 필요한 컬럼만 선택
            elif len(pop.columns) >= 2:
                pop.columns = ['무시', '자치구'] + [f'col_{i}' for i in range(2, len(pop.columns))]
                pop = pop[['자치구']]  # 자치구만 선택
            else:
                raise ValueError(f"pop 데이터 컬럼 수가 부족합니다: {len(pop.columns)}")
            
            logger.info(f"pop 컬럼 (컬럼명 설정 후): {pop.columns.tolist()}")
            
            # 행 편집: 첫 번째 행("합계", "소계") 제거
            if len(pop) > 0:
                # 첫 번째 행이 "합계"인 경우 제거
                first_row_value = str(pop.iloc[0, 0]) if len(pop.columns) > 0 else ""
                if first_row_value == "합계" or first_row_value.startswith("합계"):
                    pop = pop.drop(pop.index[0])
                    logger.info("pop 첫 번째 행('합계') 제거 완료")
            
            logger.info(f"pop 전처리 완료: {pop.shape}, 컬럼: {pop.columns.tolist()}")
            logger.info(f"pop 첫 5행:\n{pop.head()}")
            
            # '자치구' 컬럼이 있는지 최종 확인
            if '자치구' not in pop.columns:
                raise ValueError(f"pop 데이터에 '자치구' 컬럼을 찾을 수 없습니다. 현재 컬럼: {pop.columns.tolist()}")
            
            # cctv와 pop 머지
            logger.info(f"머지 시도: cctv['기관명'] vs pop['자치구']")
            logger.info(f"cctv 기관명 샘플: {cctv['기관명'].head(3).tolist() if '기관명' in cctv.columns else '기관명 컬럼 없음'}")
            logger.info(f"pop 자치구 샘플: {pop['자치구'].head(3).tolist() if '자치구' in pop.columns else '자치구 컬럼 없음'}")
            
            cctv_pop = self.method.df_merge(
                left=cctv,
                right=pop,
                left_on='기관명',
                right_on='자치구',
                how='inner'
            )
            
            # 머지 후 "기관명" 컬럼 제거 (자치구와 동일한 값이므로)
            if '기관명' in cctv_pop.columns:
                cctv_pop = cctv_pop.drop(columns=['기관명'])
            
            logger.info(f"머지 완료: cctv_pop={cctv_pop.shape}")
            
            # 경찰서 주소 검색 (카카오맵 API) - 에러 발생 시 빈 값으로 처리
            station_addrs = []
            station_lats = []
            station_lngs = []
            gu_names = []
            
            try:
                logger.info("경찰서 관서명으로 주소 검색 시작...")
                
                station_names = []  # 경찰서 관서명 리스트
                # crime 데이터에서 자치구 이름을 가져와서 경찰서명 생성
                if '자치구' in crime.columns:
                    for name in crime['자치구']:
                        if pd.notna(name) and str(name).strip():
                            station_names.append('서울' + str(name) + '경찰서')
                        else:
                            station_names.append('')
                else:
                    logger.warning("crime 데이터에 '자치구' 컬럼이 없습니다. 지도 정보를 생성할 수 없습니다.")
                    station_names = []
                
                kakao = KakaoMapSingleton()  # 카카오맵 객체 생성
                logger.info(f"총 {len(station_names)}개 경찰서 주소 검색 중...")
                
                for idx, name in enumerate(station_names, 1):
                    try:
                        tmp = kakao.geocode(name, language='ko')
                        if tmp and len(tmp) > 0:
                            formatted_addr = tmp[0].get("formatted_address", "")
                            logger.info(f"[{idx}/{len(station_names)}] {name}의 검색 결과: {formatted_addr}")
                            station_addrs.append(formatted_addr)
                            tmp_loc = tmp[0].get("geometry", {})
                            location = tmp_loc.get('location', {})
                            station_lats.append(location.get('lat', 0.0))
                            station_lngs.append(location.get('lng', 0.0))
                        else:
                            logger.warning(f"[{idx}/{len(station_names)}] {name}의 검색 결과가 없습니다.")
                            station_addrs.append("")
                            station_lats.append(0.0)
                            station_lngs.append(0.0)
                    except Exception as e:
                        logger.error(f"[{idx}/{len(station_names)}] {name} 검색 중 오류 발생: {str(e)}")
                        station_addrs.append("")
                        station_lats.append(0.0)
                        station_lngs.append(0.0)
                
                logger.info(f"주소 검색 완료. 검색된 주소 리스트: {station_addrs}")
                
                # 주소에서 자치구 추출
                for idx, addr in enumerate(station_addrs):
                    try:
                        if addr:
                            tmp = addr.split()
                            tmp_gu_list = [gu for gu in tmp if gu[-1] == '구']
                            if tmp_gu_list:
                                gu_names.append(tmp_gu_list[0])
                            else:
                                logger.warning(f"주소에서 자치구를 찾을 수 없습니다: {addr}")
                                gu_names.append("")
                        else:
                            logger.warning(f"빈 주소입니다. 자치구를 추출할 수 없습니다.")
                            gu_names.append("")
                    except Exception as e:
                        logger.error(f"자치구 추출 중 오류 발생 (주소: {addr}): {str(e)}")
                        gu_names.append("")
                        
            except Exception as e:
                logger.error(f"카카오맵 API 호출 중 전체 오류 발생: {str(e)}")
                # 에러 발생 시 빈 값으로 채우기
                station_addrs = [''] * len(crime)
                station_lats = [0.0] * len(crime)
                station_lngs = [0.0] * len(crime)
                gu_names = [''] * len(crime)
            
            # crime 원본 데이터에 자치구, 경찰서 주소, 좌표 추가
            if '자치구' not in crime.columns or crime['자치구'].isna().all():
                if len(gu_names) == len(crime):
                    crime['자치구'] = gu_names
                else:
                    crime['자치구'] = gu_names[:len(crime)] if len(gu_names) > len(crime) else gu_names + [''] * (len(crime) - len(gu_names))
            
            if len(station_addrs) == len(crime):
                crime['경찰서주소'] = station_addrs
                crime['위도'] = station_lats
                crime['경도'] = station_lngs
            else:
                crime['경찰서주소'] = station_addrs[:len(crime)] if len(station_addrs) > len(crime) else station_addrs + [''] * (len(crime) - len(station_addrs))
                crime['위도'] = station_lats[:len(crime)] if len(station_lats) > len(crime) else station_lats + [0.0] * (len(crime) - len(station_lats))
                crime['경도'] = station_lngs[:len(crime)] if len(station_lngs) > len(crime) else station_lngs + [0.0] * (len(crime) - len(station_lngs))
            
            # crime_with_location은 crime의 복사본 (이미 경찰서 정보가 포함됨)
            crime_with_location = crime.copy()

            # station_info 리스트 생성
            station_info_list = [
                {
                    "자치구": gu_name,
                    "경찰서명": station_name,
                    "주소": addr,
                    "위도": lat,
                    "경도": lng
                }
                for gu_name, station_name, addr, lat, lng in zip(
                    crime['자치구'].tolist() if '자치구' in crime.columns else [''] * len(crime),
                    station_names[:len(crime)] if station_names else [''] * len(crime),
                    station_addrs[:len(crime)],
                    station_lats[:len(crime)],
                    station_lngs[:len(crime)]
                )
            ]
            
            # CSV 파일로 저장
            save_dir = Path(self.data.dname).parent / "save"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                cctv.to_csv(save_dir / "cctv.csv", index=False, encoding='utf-8-sig')
                crime.to_csv(save_dir / "crime.csv", index=False, encoding='utf-8-sig')
                pop.to_csv(save_dir / "pop.csv", index=False, encoding='utf-8-sig')
                cctv_pop.to_csv(save_dir / "cctv_pop.csv", index=False, encoding='utf-8-sig')
                crime_with_location.to_csv(save_dir / "crime_with_location.csv", index=False, encoding='utf-8-sig')
                
                # station_info를 DataFrame으로 변환하여 저장
                if station_info_list:
                    station_df = pd.DataFrame(station_info_list)
                    station_df.to_csv(save_dir / "station_info.csv", index=False, encoding='utf-8-sig')
                
                logger.info(f"✅ CSV 파일 저장 완료: {save_dir}")
                logger.info(f"   - cctv.csv")
                logger.info(f"   - crime.csv")
                logger.info(f"   - pop.csv")
                logger.info(f"   - cctv_pop.csv")
                logger.info(f"   - crime_with_location.csv")
                logger.info(f"   - station_info.csv")
            except Exception as save_error:
                logger.warning(f"⚠️ CSV 파일 저장 중 오류 발생: {str(save_error)}")
            
            # 데이터프레임을 딕셔너리로 변환 (JSON 직렬화 가능하도록)
            result = {
                "cctv": cctv.to_dict(orient='records'),
                "crime": crime.to_dict(orient='records'),
                "pop": pop.to_dict(orient='records'),
                "cctv_pop": cctv_pop.to_dict(orient='records'),  # merge된 데이터
                "crime_with_location": crime_with_location.to_dict(orient='records'),  # 지도 정보 포함
                "cctv_shape": list(cctv.shape),
                "crime_shape": list(crime.shape),
                "pop_shape": list(pop.shape),
                "cctv_pop_shape": list(cctv_pop.shape),
                "cctv_columns": cctv.columns.tolist(),
                "crime_columns": crime.columns.tolist(),
                "pop_columns": pop.columns.tolist(),
                "cctv_pop_columns": cctv_pop.columns.tolist(),
                "crime_with_location_columns": crime_with_location.columns.tolist(),
                "station_info": station_info_list
            }
            
            logger.info("load_data() 완료")
            return result
            
        except Exception as e:
            logger.error(f"load_data() 중 오류 발생: {str(e)}", exc_info=True)
            raise

    def preprocess(self):
        try:
            data_dir = Path(self.data.dname)
            cctv_path = data_dir / "cctv.csv"
            crime_path = data_dir / "crime.csv"
            pop_path = data_dir / "pop.csv"
            
            # 데이터 로드
            cctv = self.method.csv_to_df(str(cctv_path))
            # 컬럼이 존재하는지 확인 후 삭제
            columns_to_drop = ['2013년도 이전', '2014년', '2015년', '2016년']
            existing_columns_to_drop = [col for col in columns_to_drop if col in cctv.columns]
            if existing_columns_to_drop:
                cctv = cctv.drop(existing_columns_to_drop, axis=1)
            
            # crime.csv 헤더 읽기 (3행과 4행을 조합하여 컬럼명 생성)
            crime_header_row3 = pd.read_csv(str(crime_path), skiprows=2, nrows=1, header=None, encoding='utf-8')
            crime_header_row4 = pd.read_csv(str(crime_path), skiprows=3, nrows=1, header=None, encoding='utf-8')
            
            # 컬럼명 생성: 3행과 4행을 조합 (예: "소계_발생", "살인_검거" 등)
            column_names = ['무시', '자치구']  # 첫 두 컬럼은 고정
            for i in range(2, len(crime_header_row3.columns)):
                row3_val = str(crime_header_row3.iloc[0, i]).strip() if i < len(crime_header_row3.columns) else ""
                row4_val = str(crime_header_row4.iloc[0, i]).strip() if i < len(crime_header_row4.columns) else ""
                if row3_val and row4_val:
                    column_names.append(f"{row3_val}_{row4_val}")
                elif row3_val:
                    column_names.append(row3_val)
                elif row4_val:
                    column_names.append(row4_val)
                else:
                    column_names.append(f'col_{i}')
            
            # crime.csv는 첫 4행이 헤더이므로 skiprows=4 사용
            crime = pd.read_csv(str(crime_path), skiprows=4, header=None, encoding='utf-8')
            # 컬럼명 설정
            if len(crime.columns) >= 2:
                # 컬럼 수에 맞게 조정
                final_column_names = column_names[:len(crime.columns)]
                if len(final_column_names) < len(crime.columns):
                    final_column_names += [f'col_{i}' for i in range(len(final_column_names), len(crime.columns))]
                crime.columns = final_column_names
                # 첫 번째 행("합계", "소계") 제거
                if len(crime) > 0 and str(crime.iloc[0, 0]) == "합계":
                    crime = crime.drop(crime.index[0])
            else:
                raise ValueError(f"crime 데이터 컬럼 수가 부족합니다: {len(crime.columns)}")
            
            # pop.csv는 첫 3행이 헤더이므로 skiprows=3 사용
            pop = pd.read_csv(str(pop_path), skiprows=3, header=None, encoding='utf-8')
            # 컬럼명 설정: 첫 번째 컬럼은 무시, 두 번째가 자치구, 네 번째가 인구수
            if len(pop.columns) >= 4:
                pop.columns = ['무시', '자치구', '무시2', '인구수'] + [f'col_{i}' for i in range(4, len(pop.columns))]
                # 컬럼 편집: 자치구(인덱스 1)와 좌로부터 4번째 컬럼(인덱스 3)만 남기기
                columns_to_keep = [pop.columns[1], pop.columns[3]]  # 자치구와 좌로부터 4번째 컬럼
                pop = pop[columns_to_keep]
                # 컬럼명 재설정
                pop.columns = ['자치구', '인구수']
            elif len(pop.columns) >= 2:
                pop.columns = ['무시', '자치구'] + [f'col_{i}' for i in range(2, len(pop.columns))]
                pop = pop[['자치구']]  # 자치구만 선택
            else:
                raise ValueError(f"pop 데이터 컬럼 수가 부족합니다: {len(pop.columns)}")
            
            # pop 첫 번째 행("합계", "소계") 제거
            if len(pop) > 0:
                first_row_value = str(pop.iloc[0, 0]) if len(pop.columns) > 0 else ""
                if first_row_value == "합계" or first_row_value.startswith("합계"):
                    pop = pop.drop(pop.index[0])
            
            # 행 편집: 위로부터 2, 3, 4 번째 행 제거 (인덱스 1, 2, 3)
            # 인덱스가 충분한지 확인 후 제거
            if len(pop) > 3:
                pop = pop.drop(pop.index[1:4])  # 인덱스 1, 2, 3 제거
            elif len(pop) > 1:
                # 인덱스가 부족하면 가능한 만큼만 제거
                pop = pop.drop(pop.index[1:])
            
            logger.info(f"  cctv 탑  : {cctv.head(1).to_string()}")
            logger.info(f"  crime 탑  : {crime.head(1).to_string()}")
            logger.info(f"  pop 탑  : {pop.head(1).to_string()}")
            
            # cctv와 pop 머지 전략
            # - cctv의 "기관명"과 pop의 "자치구"를 키로 사용
            # - 중복된 feature가 없도록 처리
            # - "기관명"과 "자치구"는 같은 값이지만 컬럼명이 다르므로 left_on, right_on 사용
            
            # 머지 전에 컬럼명 확인 및 중복 컬럼 체크
            logger.info(f"cctv 컬럼: {cctv.columns.tolist()}")
            logger.info(f"pop 컬럼: {pop.columns.tolist()}")
            
            # 중복되는 컬럼 확인 (키 컬럼 제외)
            cctv_cols = set(cctv.columns) - {'기관명'}
            pop_cols = set(pop.columns) - {'자치구'}
            duplicate_cols = cctv_cols & pop_cols
            
            if duplicate_cols:
                logger.warning(f"중복되는 컬럼이 발견되었습니다: {duplicate_cols}")
                logger.info("머지 시 suffixes를 사용하여 중복 컬럼을 구분합니다.")
            
            # cctv의 "기관명"과 pop의 "자치구"를 키로 머지
            cctv_pop = self.method.df_merge(
                left=cctv,
                right=pop,
                left_on='기관명',
                right_on='자치구',
                how='inner'
            )
            
            # 머지 후 "기관명" 또는 "자치구" 컬럼 제거 (중복이므로)
            # '기관명'이 있으면 제거, 없으면 '자치구' 제거
            if '기관명' in cctv_pop.columns:
                cctv_pop = cctv_pop.drop(columns=['기관명'])
            elif '자치구' in cctv_pop.columns:
                # '기관명'이 없으면 '자치구'를 '기관명'으로 이름 변경 (일관성 유지)
                cctv_pop = cctv_pop.rename(columns={'자치구': '기관명'})
            
            logger.info(f"머지 완료: cctv_pop shape = {cctv_pop.shape}")
            logger.info(f"cctv_pop 컬럼: {cctv_pop.columns.tolist()}")
            logger.info(f"cctv_pop 탑 :\n{cctv_pop.head(1).to_string()}")

            # 관서명에 따른 경찰서 주소 찾기
            logger.info("경찰서 관서명으로 주소 검색 시작...")
            
            station_names = [] # 경찰서 관서명 리스트
            # crime 데이터에서 자치구 이름을 가져와서 경찰서명 생성
            if '자치구' in crime.columns:
                for name in crime['자치구']:
                    if pd.notna(name) and str(name).strip() and str(name) != '소계':
                        # 키워드 검색에 적합한 형식: "{구}경찰서" (예: "마포경찰서")
                        station_names.append(f'{str(name).strip()}경찰서')
                    else:
                        station_names.append('')
            else:
                logger.warning("crime 데이터에 '자치구' 컬럼이 없습니다.")
                station_names = []
            logger.info(f"경찰서 관서명 리스트: {station_names}")
            
            station_addrs = []
            station_lats = []
            station_lngs = []
            
            # 싱글턴 패턴 테스트
            kakao1 = KakaoMapSingleton()
            kakao2 = KakaoMapSingleton()
            if kakao1 is kakao2:
                logger.info("KakaoMapSingleton: 동일한 객체입니다 (싱글턴 패턴 정상 작동)")
            else:
                logger.warning("KakaoMapSingleton: 다른 객체입니다 (싱글턴 패턴 오류)")
            
            kakao = KakaoMapSingleton() # 카카오맵 객체 생성
            logger.info(f"총 {len(station_names)}개 경찰서 주소 검색 중...")
            
            for idx, name in enumerate(station_names, 1):
                try:
                    # 키워드 검색에 적합한 여러 검색 쿼리 형식 시도
                    search_queries = [
                        name,  # 원본: "종로구경찰서"
                        f"서울{name}",  # "서울종로구경찰서"
                        f"서울시 {name.replace('경찰서', ' 경찰서')}",  # "서울시 종로구 경찰서"
                        name.replace("구", ""),  # "종로경찰서" (구 제거)
                    ]
                    
                    tmp = None
                    used_query = None
                    for query in search_queries:
                        tmp = kakao.geocode(query, language='ko')
                        if tmp and len(tmp) > 0:
                            used_query = query
                            break
                    
                    if tmp and len(tmp) > 0:
                        formatted_addr = tmp[0].get("formatted_address", "")
                        logger.info(f"[{idx}/{len(station_names)}] {name} (검색 쿼리: {used_query}) → {formatted_addr}")
                        station_addrs.append(formatted_addr)
                        tmp_loc = tmp[0].get("geometry", {})
                        location = tmp_loc.get('location', {})
                        station_lats.append(location.get('lat', 0.0))
                        station_lngs.append(location.get('lng', 0.0))
                    else:
                        logger.warning(f"[{idx}/{len(station_names)}] {name}의 검색 결과가 없습니다. (시도한 쿼리: {search_queries})")
                        station_addrs.append("")
                        station_lats.append(0.0)
                        station_lngs.append(0.0)
                except Exception as e:
                    logger.error(f"[{idx}/{len(station_names)}] {name} 검색 중 오류 발생: {str(e)}")
                    station_addrs.append("")
                    station_lats.append(0.0)
                    station_lngs.append(0.0)
            
            logger.info(f"주소 검색 완료. 검색된 주소 리스트: {station_addrs}")
            
            # 주소에서 자치구 추출
            gu_names = []
            for idx, addr in enumerate(station_addrs):
                try:
                    if addr:
                        tmp = addr.split()
                        tmp_gu_list = [gu for gu in tmp if gu[-1] == '구']
                        if tmp_gu_list:
                            gu_names.append(tmp_gu_list[0])
                        else:
                            logger.warning(f"주소에서 자치구를 찾을 수 없습니다: {addr}")
                            gu_names.append("")
                    else:
                        logger.warning(f"빈 주소입니다. 자치구를 추출할 수 없습니다.")
                        gu_names.append("")
                except Exception as e:
                    logger.error(f"자치구 추출 중 오류 발생 (주소: {addr}): {str(e)}")
                    gu_names.append("")
            
            logger.info(f"추출된 자치구 리스트: {gu_names}")
            
            # crime 데이터프레임에 자치구 컬럼 추가
            if len(gu_names) == len(crime):
                crime['자치구'] = gu_names
                logger.info("crime 데이터프레임에 '자치구' 컬럼이 추가되었습니다.")
            else:
                logger.warning(f"자치구 리스트 길이({len(gu_names)})와 crime 데이터 길이({len(crime)})가 일치하지 않습니다.")
                # 길이가 다르더라도 가능한 만큼만 추가
                crime['자치구'] = gu_names[:len(crime)] if len(gu_names) > len(crime) else gu_names + [''] * (len(crime) - len(gu_names))

            logger.info("카카오맵 실행 완료")
            
            # 전체 데이터 머지: cctv_pop + crime (자치구 기준)
            # cctv_pop에는 '자치구' 또는 '기관명' 컬럼이 있고, crime에도 '자치구' 컬럼이 있음
            merged_all = None
            try:
                # cctv_pop의 키 컬럼 확인
                cctv_pop_key = '기관명' if '기관명' in cctv_pop.columns else '자치구'
                crime_key = '자치구'
                
                # crime에 경찰서 정보가 있으면 머지
                if crime_key in crime.columns and cctv_pop_key in cctv_pop.columns:
                    merged_all = self.method.df_merge(
                        left=cctv_pop,
                        right=crime,
                        left_on=cctv_pop_key,
                        right_on=crime_key,
                        how='left'
                    )
                    logger.info(f"전체 데이터 머지 완료: {merged_all.shape}")
                else:
                    logger.warning("머지할 키 컬럼이 없어 cctv_pop만 사용합니다.")
                    merged_all = cctv_pop
            except Exception as merge_error:
                logger.warning(f"전체 데이터 머지 중 오류 발생: {str(merge_error)}, cctv_pop만 사용합니다.")
                merged_all = cctv_pop
            
            return {
                "status": "success",
                "cctv_rows": len(cctv),
                "cctv_columns": cctv.columns.tolist(),
                "crime_rows": len(crime),
                "crime_columns": crime.columns.tolist(),
                "pop_rows": len(pop),
                "pop_columns": pop.columns.tolist(),
                "cctv_pop_rows": len(cctv_pop),
                "cctv_pop_columns": cctv_pop.columns.tolist(),
                "merged_all_rows": len(merged_all) if merged_all is not None else 0,
                "merged_all_columns": merged_all.columns.tolist() if merged_all is not None else [],
                "merged_all": merged_all.to_dict(orient='records') if merged_all is not None else [],
                "cctv_preview": cctv.head(3).to_dict(orient='records'),
                "crime_preview": crime.head(3).to_dict(orient='records'),
                "pop_preview": pop.head(3).to_dict(orient='records'),
                "cctv_pop_preview": cctv_pop.head(3).to_dict(orient='records'),
                "message": "데이터 전처리 및 머지가 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"preprocess() 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def create_heatmap(self, crime_type: str = 'total', save_path: str = None):
        """
        서울 범죄 데이터 히트맵 생성
        
        Args:
            crime_type: 범죄 유형 ('total', '살인', '강도', '강간', '절도', '폭력')
            save_path: 저장 경로 (None이면 기본 경로에 저장)
        
        Returns:
            히트맵 HTML 파일 경로
        """
        # 런타임에 folium import 시도 (모듈 레벨 변수보다 우선)
        try:
            import folium
            from folium.plugins import HeatMap
        except ImportError as e:
            raise ImportError(f"folium 라이브러리가 설치되지 않았습니다: {str(e)}. 'pip install folium'으로 설치해주세요.")
        
        try:
            # 데이터 로드
            data_dir = Path(self.data.dname)
            crime_path = data_dir / "crime.csv"
            
            # crime.csv 헤더 읽기
            crime_header_row3 = pd.read_csv(str(crime_path), skiprows=2, nrows=1, header=None, encoding='utf-8')
            crime_header_row4 = pd.read_csv(str(crime_path), skiprows=3, nrows=1, header=None, encoding='utf-8')
            
            # 컬럼명 생성
            column_names = ['무시', '자치구']
            for i in range(2, len(crime_header_row3.columns)):
                row3_val = str(crime_header_row3.iloc[0, i]).strip() if i < len(crime_header_row3.columns) else ""
                row4_val = str(crime_header_row4.iloc[0, i]).strip() if i < len(crime_header_row4.columns) else ""
                if row3_val and row4_val:
                    column_names.append(f"{row3_val}_{row4_val}")
                elif row3_val:
                    column_names.append(row3_val)
                elif row4_val:
                    column_names.append(row4_val)
                else:
                    column_names.append(f'col_{i}')
            
            # crime 데이터 로드
            crime = pd.read_csv(str(crime_path), skiprows=4, header=None, encoding='utf-8')
            if len(crime.columns) >= 2:
                final_column_names = column_names[:len(crime.columns)]
                if len(final_column_names) < len(crime.columns):
                    final_column_names += [f'col_{i}' for i in range(len(final_column_names), len(crime.columns))]
                crime.columns = final_column_names
                if len(crime) > 0 and str(crime.iloc[0, 0]) == "합계":
                    crime = crime.drop(crime.index[0])
            
            # 경찰서 주소 및 좌표 가져오기
            kakao = KakaoMapSingleton()
            station_lats = []
            station_lngs = []
            crime_values = []
            gu_names = []
            
            # 범죄 데이터 컬럼 찾기
            crime_col = None
            if crime_type == 'total':
                # 전체 범죄 발생 건수 계산
                crime_cols = [col for col in crime.columns if '발생' in col and any(c in col for c in self.crime_columns)]
                if crime_cols:
                    # 숫자형으로 변환 후 합계 계산
                    for col in crime_cols:
                        crime[col] = pd.to_numeric(crime[col], errors='coerce').fillna(0)
                    crime['총범죄'] = crime[crime_cols].sum(axis=1)
                    crime_col = '총범죄'
            else:
                # 특정 범죄 유형 찾기
                crime_col = None
                for col in crime.columns:
                    if crime_type in col and '발생' in col:
                        crime_col = col
                        break
                
                if not crime_col:
                    raise ValueError(f"범죄 유형 '{crime_type}'에 해당하는 컬럼을 찾을 수 없습니다.")
            
            logger.info(f"히트맵 생성 시작: 범죄 유형={crime_type}, 컬럼={crime_col}")
            
            # 각 자치구별로 경찰서 좌표 및 범죄 건수 수집
            for idx, row in crime.iterrows():
                gu_name = str(row['자치구']).strip() if '자치구' in row and pd.notna(row['자치구']) else None
                
                if not gu_name or gu_name == '소계' or gu_name == '':
                    continue
                
                # 경찰서 주소 검색
                station_name = f'{gu_name}경찰서'
                try:
                    tmp = kakao.geocode(station_name, language='ko')
                    if tmp and len(tmp) > 0:
                        tmp_loc = tmp[0].get("geometry", {})
                        location = tmp_loc.get('location', {})
                        lat = location.get('lat', 0.0)
                        lng = location.get('lng', 0.0)
                        
                        if lat != 0.0 and lng != 0.0:
                            station_lats.append(lat)
                            station_lngs.append(lng)
                            
                            # 범죄 건수 (숫자형으로 변환)
                            crime_value = row[crime_col] if crime_col in row and pd.notna(row[crime_col]) else 0
                            try:
                                crime_value = float(pd.to_numeric(crime_value, errors='coerce')) if pd.notna(crime_value) else 0.0
                            except (ValueError, TypeError):
                                crime_value = 0.0
                            crime_values.append(crime_value)
                            gu_names.append(gu_name)
                except Exception as e:
                    logger.warning(f"{station_name} 검색 중 오류: {str(e)}")
                    continue
            
            if len(station_lats) == 0:
                raise ValueError("경찰서 좌표를 찾을 수 없습니다.")
            
            # 서울 중심 좌표
            seoul_center = [37.5665, 126.9780]
            
            # Folium 지도 생성
            m = folium.Map(
                location=seoul_center,
                zoom_start=11,
                tiles='OpenStreetMap'
            )
            
            # 히트맵 데이터 준비 (위도, 경도, 가중치)
            heat_data = [[lat, lng, weight] for lat, lng, weight in zip(station_lats, station_lngs, crime_values)]
            
            # 히트맵 추가
            HeatMap(
                heat_data,
                min_opacity=0.2,
                max_zoom=18,
                radius=25,
                blur=15,
                gradient={
                    0.2: 'blue',
                    0.4: 'cyan',
                    0.6: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'
                }
            ).add_to(m)
            
            # 마커 추가 (자치구별 범죄 건수 표시)
            for lat, lng, value, gu in zip(station_lats, station_lngs, crime_values, gu_names):
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=8,
                    popup=f"{gu}<br>{crime_type}: {value:,.0f}건",
                    color='black',
                    fill=True,
                    fillColor='red' if value > np.percentile(crime_values, 75) else 'orange' if value > np.percentile(crime_values, 50) else 'yellow',
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m)
            
            # 저장 경로 설정
            if save_path is None:
                save_dir = Path(self.data.sname)
                save_dir.mkdir(parents=True, exist_ok=True)
                save_path = save_dir / f"crime_heatmap_{crime_type}.html"
            else:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # HTML 파일로 저장
            m.save(str(save_path))
            logger.info(f"히트맵이 저장되었습니다: {save_path}")
            
            # 절대 경로와 웹 URL 생성
            absolute_path = save_path.resolve()
            file_name = save_path.name
            
            return {
                "status": "success",
                "file_path": str(save_path),
                "absolute_path": str(absolute_path),
                "file_name": file_name,
                "web_url": f"/static/heatmap/{file_name}",
                "crime_type": crime_type,
                "districts_count": len(gu_names),
                "total_crimes": sum(crime_values),
                "message": f"{crime_type} 범죄 히트맵이 성공적으로 생성되었습니다",
                "instructions": {
                    "local_file": f"파일 탐색기에서 다음 경로를 열거나 브라우저로 드래그하세요: {absolute_path}",
                    "web_url": f"서버가 실행 중이면 다음 URL로 접근하세요: http://localhost:9010/static/heatmap/{file_name}"
                }
            }
            
        except Exception as e:
            logger.error(f"히트맵 생성 중 오류 발생: {str(e)}", exc_info=True)
            raise
         