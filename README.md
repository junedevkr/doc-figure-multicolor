# doc-figure-multicolor

[doc-figure](https://github.com/parkjui92/doc-figure)를 포크해 **멀티 컬러차트와 색 체계, 16:9 발표 덱**을 더한 업데이트판. 스킬 이름과 설치 폴더도 `doc-figure-multicolor`.

## 이번 업데이트

- **멀티 컬러차트**: 공개 프레젠테이션 팔레트 28개(P-01~P-28)를 같은 미니 슬라이드에 입혀 비교하고 번호로 골라 컨셉으로 만든다
- **컬러 컨셉**: `jf-timeless`(P-01 남색·하늘색·노랑), `jf-serene`(P-02 파스텔), `jf-pop`(쨍한 컨셉)
- **내용 계열 색 7가지 + 흑백톤**: 논문 제목·초록으로 계열을 판별
- **16:9 발표 덱**: 여러 장을 HTML 하나로, 화살표·페이지 번호·전체화면·PDF
- **글자 대비 자동 보정**, 글자 값 표 전폭 표시
- **시작 질문**: 스킬을 부르면 글꼴(고딕·명조)과 발표 색상 컨셉을 먼저 묻는다
- 원본 doc-figure v2.4(데이터 그래프·디자인 보고서풍 구조도)까지 병합, 원본 갱신은 주기적으로 병합

## 개요

논문발표 PT·도식용 Claude Code 스킬. [parkjui92/doc-figure](https://github.com/parkjui92/doc-figure)(MIT)를 포크해 색 체계·페이지 틀·발표용 덱을 더했다. 도식 문법·레시피·`--verify` 점검과 원본 v2.4의 데이터 그래프(viz)·디자인 보고서풍 구조도는 원본을 그대로 쓴다. 원본 갱신은 주기적으로 병합한다. 원본 설명은 [README.doc-figure.md](README.doc-figure.md).

## 원본에서 달라진 것

| 영역 | 내용 |
|---|---|
| 색 | 논문 내용 계열 팔레트 7가지(`jf-policy` `jf-tech` `jf-method` `jf-risk` `jf-social` `jf-economy` `jf-green`), 흑백톤(`jf-mono-ink` `jf-mono-warm` `jf-mono-spot-<계열>`), 컬러 컨셉(`jf-pop` 쨍한 컨셉, `jf-serene` P-02 파스텔, `jf-timeless` P-01 남색·노랑) |
| 색 고르기 | `jf_palette.py pick`이 제목·초록 키워드로 계열을 판별. 새 컨셉은 컬러차트(공개 프레젠테이션 팔레트 28개)에서 골라 만든다 |
| 제목 | 논문의 장·절 번호 + 짧은 제목(`3 구제역 사태의 전개과정`). 원본의 결론형 문장 제목은 쓰지 않음 |
| 페이지 | 16:9(1920×1080 기준), 비율을 유지한 채 화면 폭에 맞춤. 여백 64px·내용 폭 1792px 고정, 제목 42px 고정, 바깥 배경과 페이지 색 분리, 높이 88~100%를 채우도록 자동 조정 |
| 글꼴 | 고딕 = 프리젠테이션(Freesentation) 웹폰트(기본), 명조 = Noto Serif KR. `--font gothic|myeongjo`. 글꼴을 내려받은 뒤 도식을 그림 |
| 덱 | 여러 장을 HTML 하나로. 화살표·페이지 번호·키보드 이동, 전체화면 발표(조작 막대 없음, 클릭·키보드로 넘김), 하단 페이지 번호·논문 제목, PDF는 페이지마다 1920×1080 한 장 |
| 대비 | 그린 뒤 글자와 실제 바탕의 대비를 재서 모자라면 글자색 자동 보정(알약·꼬리표 포함). 글자 값 표는 폭을 채우는 표로 |
| 장식 | 카드·셀 옆 세로 색 막대는 쓰지 않음 |
| 빌드 | 크롬·파이썬 패키지 없이 표준 라이브러리만으로 HTML을 만든다(`jf_build_html.py`, `jf_build_deck.py`) |

## 설치

```bash
git clone https://github.com/junedevkr/doc-figure-multicolor ~/.claude/skills/doc-figure-multicolor
```

## 쓰는 법

```bash
# 내용 계열 판별
python3 scripts/jf_palette.py pick --text "논문 제목과 초록"

# 한 장
python3 scripts/jf_build_html.py 그림_01.json

# 여러 장 덱 (모든 페이지 프리셋을 한 번에 바꾸려면 --preset)
python3 scripts/jf_build_deck.py 그림_01.json 그림_02.json -o 페이지모음.html --title "제목" --footer "논문 제목" --preset jf-serene --font myeongjo

# 컬러차트 (공개 팔레트 28개를 미니 슬라이드에 입혀 비교, 번호로 고름)
python3 scripts/jf_color_chart.py -o 컬러차트.html

# 팔레트 고친 뒤
python3 scripts/jf_palette.py build && python3 scripts/jf_palette.py check
```

덱 단축키: ← → · Space 넘김, F 전체화면, N 하단 페이지 번호 보이기·숨기기, Esc 전체화면 끝.

## 파일

| 경로 | 내용 |
|---|---|
| `SKILL.md` | 스킬 본문. 앞부분 'doc-figure-multicolor 규칙' 1~5절이 원본과 다른 규칙 |
| `references/jf-color-system.md` | 색 체계·컨셉·tone 뜻 |
| `references/jf-palettes.json` | 계열 팔레트·컨셉 원본 값 |
| `references/jf-source-palettes.json` | 컬러차트용 팔레트 28개(P-01~P-28) |
| `references/jf-font.css` | 프리젠테이션 웹폰트 |
| `scripts/jf_palette.py` | 프리셋 생성·대비/구별 검사·판별·PT 테마 JSON·미리보기 |
| `scripts/jf_page.py` | 16:9 페이지 틀·글꼴·자동 맞춤 |
| `scripts/jf_build_html.py` · `jf_build_deck.py` | 한 장·덱 빌드 |
| `scripts/jf_color_chart.py` | 컬러차트 |
| `examples/jf-demo/` | 더미 데이터 도식 7장(연구 질문·분석틀·자료와 절차·집단별 변화·판단 경로·2×2·단계별 제언) |
| `원본출처.md` | 포크 시점과 변경 기록 |

## 라이선스

MIT. 원본 저작권 표기(parkjui92)는 [LICENSE](LICENSE)에 그대로 둔다. 아이콘은 Tabler Icons(MIT), 글꼴은 프리젠테이션(눈누 배포) 웹폰트를 CDN으로 불러온다.
