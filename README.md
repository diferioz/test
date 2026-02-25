# 투자 기록 CLI (국내/국외 ETF & 주식)

국내/국외 ETF 및 주식 투자 정보를 기록하고, 시세 업데이트에 따라 평가금액/손익을 확인할 수 있는 간단한 CLI 도구입니다.

## 기능

- 자산 추가 (`add`)
- 현재가 업데이트 (`update-price`)
- 보유 자산 및 통화별 요약 조회 (`list`)

## 빠른 시작

```bash
python3 app.py add \
  --symbol 069500 \
  --market KR \
  --asset-type ETF \
  --quantity 10 \
  --avg-buy-price 35000 \
  --current-price 36200 \
  --currency KRW

python3 app.py add \
  --symbol VTI \
  --market US \
  --asset-type ETF \
  --quantity 3 \
  --avg-buy-price 240 \
  --current-price 255 \
  --currency USD

python3 app.py list
python3 app.py update-price --symbol VTI --market US --current-price 260
python3 app.py list
```

기본 저장 파일은 `portfolio.json`이며, `--db` 옵션으로 파일 경로를 바꿀 수 있습니다.
