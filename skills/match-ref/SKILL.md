---
name: match-ref
description: 완성된 마스터 하나를 레퍼런스 곡에 맞춘다 — 3자 실측 대조 → 후보 2개 브래킷 → 사람이 고름 → 확정. 스템이 아니라 이미 섞인 2채널이 입력이다.
disable-model-invocation: true
---

`$ARGUMENTS` = `<타깃 파일> <레퍼런스 파일> [--lufs -10] [--tp -1.0]`

```
/paul:match-ref ./master.wav "./ref/Gnome - Bulls of Bravik.wav"
/paul:match-ref ./final-M2.wav ./ref/x.flac --lufs -9
```

**레퍼런스가 없으면 진단하지 않는다. 달라고 하고 멈춘다.** 이 명령이 존재하는 이유가 그거다 —
레퍼런스 없이 절대 임계로 판정했다가 실제로 틀렸다(`mix-from-stems` 공간 감사 절의 반증표).

`$ARGUMENTS` 가 비어 있거나 인자가 하나뿐이면 **무엇을 무엇에 맞출지 먼저 묻는다.**
레퍼런스는 **같은 장르 · 편성**을 요구한다. 편성이 다르면 그 사실을 먼저 알리고 사용자가 정하게 한다.

## 경계

| | |
|---|---|
| **이 스킬** | 이미 섞인 2채널 마스터를 *지정된 레퍼런스*에 맞춘다. 후보를 굽고 **사람이 고른다** |
| `mix-from-stems` | 스템 여러 개에서 믹스를 만든다. 측정 레시피 · 함정의 정본 |
| `/master-audio` (paul-rockstar) | 레퍼런스 없이 **자동 판정**해 일괄 마스터링. 청취 루프 없음 |

측정 명령·함정은 여기 다시 쓰지 않는다 — `mix-from-stems` 가 정본이다.

## 절차

```
1. 3자 측정   타깃 · (있으면) 사용자가 예전에 만든 마스터 · 레퍼런스
              I / LRA / TP / 전대역 상관도 / 모노 손실 + 9대역 에너지 + 6대역 S−M
2. 델타 산출   1k–2k 로 정렬하고 라우드니스 오프셋을 뺀 뒤 대역별 차를 낸다
3. 축 판정     톤 · S−M 기울기 · 밀도 중 무엇이 벌어졌나. 10 dB 넘는 대역은 스템 문제로 보고
4. 후보 2개    보수안 · 적극안. 같은 LUFS · 같은 TP 로 정규화 (안 맞추면 큰 게 이긴다)
5. 청취 루프   사람이 고른다 → 남은 오차 **하나만** 고쳐 다시 2개 → 수렴할 때까지
6. 확정       배포 게이트(I ±1 · TP ≤ 타깃) + 체인 레시피를 출력하고 멈춘다
```

**4번을 건너뛰지 않는다.** 한 개만 구우면 "이게 맞나"를 물을 수 없고, 세 개 넘게 구우면 고르지 못한다.
**5번에서 한 라운드에 두 가지를 동시에 고치지 않는다** — 어느 쪽이 효과였는지 사라진다.
실제로 이 루프를 7라운드 돌려 수렴시켰다.

파일은 `<타깃 폴더>/candidates/` 에 쓴다. 확정본만 타깃 폴더로 올린다.

## 3자 대조표

셸은 **`bash -c` 로 감싼다**(zsh 워드 스플리팅 — `mix-from-stems` 함정 3).

```bash
bd(){ ffmpeg -hide_banner -nostats -i "$1" -af \
 "highpass=f=$2:poles=2,highpass=f=$2:poles=2,lowpass=f=$3:poles=2,lowpass=f=$3:poles=2,astats=metadata=0" \
 -f null - 2>&1 | sed -n "/Overall/,\$p" | grep "RMS level" | awk "{printf \"%.1f\", \$NF}"; }

sm(){ bp="highpass=f=$2:poles=2,highpass=f=$2:poles=2,lowpass=f=$3:poles=2,lowpass=f=$3:poles=2"
  m=$(ffmpeg -hide_banner -nostats -i "$1" -af "pan=mono|c0=0.5*c0+0.5*c1,$bp,astats=metadata=0" -f null - 2>&1 \
      | sed -n "/Overall/,\$p" | grep "RMS level" | awk "{print \$NF}")
  s=$(ffmpeg -hide_banner -nostats -i "$1" -af "pan=mono|c0=0.5*c0-0.5*c1,$bp,astats=metadata=0" -f null - 2>&1 \
      | sed -n "/Overall/,\$p" | grep "RMS level" | awk "{print \$NF}")
  awk -v m="$m" -v s="$s" "BEGIN{printf \"%.1f\", s-m}"; }
```

대역 에너지는 `20-60 60-120 120-250 250-500 500-1000 1000-2000 2000-4000 4000-8000 8000-16000`,
S−M 은 `20-80 80-250 250-800 800-2500 2500-6000 6000-14000` 로 낸다.

## 처리 레시피

순서는 **EQ → M/S → 글루 → 서브 컴프 → 리미터**다. 실제로 수렴한 값이 아래고, 출발점으로만 쓴다.

```bash
# 1. 톤 — 레퍼런스 델타를 건다. 서브는 ±4 클램프를 넘겨도 되지만 14번 함정을 같이 읽는다
EQ="bass=g=4.0:f=110:w=0.5,equalizer=f=42:width_type=o:width=1.4:g=10.5,\
equalizer=f=180:width_type=o:width=1.0:g=2.2,equalizer=f=350:width_type=o:width=1.0:g=1.5,\
equalizer=f=700:width_type=o:width=1.1:g=-1.5,treble=g=-4.5:f=9000:w=0.5"

# 2. M/S — 저역 모노화 + 대역별 사이드. 셸프 금지, 피킹만 (함정 13)
SIDE="pan=mono|c0=0.5*c0-0.5*c1,\
highpass=f=78:poles=2,highpass=f=78:poles=2,highpass=f=78:poles=2,\
equalizer=f=150:width_type=o:width=1.0:g=5.0,equalizer=f=450:width_type=o:width=1.2:g=1.5,\
treble=g=2.5:f=900:w=0.6"
GLUE="acompressor=threshold=-16dB:ratio=2:attack=25:release=250:makeup=1.5"
SUB="acompressor=threshold=-26dB:ratio=4:attack=8:release=120:makeup=4"

ffmpeg -y -i "$SRC" -filter_complex \
 "[0:a]$EQ,asplit=2[a][b];[a]pan=mono|c0=0.5*c0+0.5*c1[m];[b]$SIDE[s];\
  [m][s]amerge=inputs=2,pan=stereo|c0=c0+c1|c1=c0-c1,$GLUE,asplit=2[lo][hi];\
  [lo]lowpass=f=80:poles=2,lowpass=f=80:poles=2,$SUB[loc];\
  [hi]highpass=f=80:poles=2,highpass=f=80:poles=2[hic];\
  [loc][hic]amix=inputs=2:normalize=0[out]" -map "[out]" -c:a pcm_s24le pre.wav
```

M/S 복원은 `M+S=L · M−S=R` 이라 `amerge` → `pan=stereo|c0=c0+c1|c1=c0-c1` 이면 끝난다.
80 Hz 분리는 LR4(2극 ×2) 라 합하면 크기가 평탄하다.

```bash
# 3. 2패스 정규화 + 오버샘플링 TP 리미터. resampler=soxr 는 없을 수 있다 — 기본값을 쓴다
LIM="aresample=176400,alimiter=limit=0.8414:attack=5:release=60:level=disabled,aresample=44100"
# I 를 재고 → volume 보정 → 리미터 → 다시 재고 → 보정. 두 번이면 ±0.1 LUFS 안에 든다
```

리미터를 **두 번 통과시키지 않는다** — LRA 가 한 번 더 깎인다(2.5 → 2.0 을 실측했다).
게인만 다시 계산해 **프리마스터에서 한 번만** 건다.

## 보고

매 라운드 표 두 개만 낸다 — **대역 에너지**와 **S−M**, 각각 `타깃 / 후보들 / 레퍼런스` 열.
맞은 칸은 `✅`, 넘친 칸은 `⚠️` 로 표시하고 **다음에 고칠 오차 하나를 지목**한다.

확정할 때 내는 것:

1. 최종 경로 + 배포 게이트 (샘플레이트 · 비트 · I · TP · 클리핑 수 · 모노 손실)
2. 원본 대비 바뀐 값 표
3. **체인 레시피** — 다른 곡에 다시 걸 수 있게 필터 값 전부

## 멈추는 자리

- 레퍼런스가 없을 때 · 편성이 명백히 다를 때
- 대역 차가 **10 dB 를 넘을 때** — EQ 로 못 만든다. 스템에서 와야 한다고 보고한다
- 후보를 고른 뒤 — **확정은 사용자가 말할 때만 한다.** 파일을 타깃 폴더로 올리지 않는다
- `candidates/` 를 **지우지 않는다.** 정리 여부도 물어본다
