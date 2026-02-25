#!/usr/bin/env python3
"""ETF/주식 투자 기록 및 자산 요약 CLI."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


DEFAULT_DB = Path("portfolio.json")


@dataclass
class Holding:
    symbol: str
    market: str
    asset_type: str
    quantity: float
    avg_buy_price: float
    current_price: float
    currency: str

    @property
    def invested_amount(self) -> float:
        return self.quantity * self.avg_buy_price

    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return self.current_value - self.invested_amount

    @property
    def profit_loss_rate(self) -> float:
        if self.invested_amount == 0:
            return 0.0
        return (self.profit_loss / self.invested_amount) * 100


class PortfolioDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.holdings: List[Holding] = []
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            self.holdings = []
            return
        data = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.holdings = [Holding(**item) for item in data.get("holdings", [])]

    def save(self) -> None:
        payload = {"holdings": [asdict(h) for h in self.holdings]}
        self.db_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_holding(self, holding: Holding) -> None:
        for h in self.holdings:
            if h.symbol == holding.symbol and h.market == holding.market:
                raise ValueError(f"이미 존재하는 종목입니다: {holding.market}:{holding.symbol}")
        self.holdings.append(holding)
        self.save()

    def update_price(self, symbol: str, market: str, price: float) -> None:
        for h in self.holdings:
            if h.symbol == symbol and h.market == market:
                h.current_price = price
                self.save()
                return
        raise ValueError(f"해당 종목을 찾을 수 없습니다: {market}:{symbol}")

    def summary_by_currency(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for h in self.holdings:
            bucket = summary.setdefault(
                h.currency,
                {"invested": 0.0, "current": 0.0, "profit_loss": 0.0},
            )
            bucket["invested"] += h.invested_amount
            bucket["current"] += h.current_value
            bucket["profit_loss"] += h.profit_loss
        return summary


def format_money(value: float) -> str:
    return f"{value:,.2f}"


def cmd_add(args: argparse.Namespace, db: PortfolioDB) -> None:
    holding = Holding(
        symbol=args.symbol.upper(),
        market=args.market.upper(),
        asset_type=args.asset_type.upper(),
        quantity=args.quantity,
        avg_buy_price=args.avg_buy_price,
        current_price=args.current_price,
        currency=args.currency.upper(),
    )
    db.add_holding(holding)
    print(f"추가 완료: {holding.market}:{holding.symbol}")


def cmd_update(args: argparse.Namespace, db: PortfolioDB) -> None:
    db.update_price(args.symbol.upper(), args.market.upper(), args.current_price)
    print(f"시세 업데이트 완료: {args.market.upper()}:{args.symbol.upper()} -> {args.current_price}")


def cmd_list(_: argparse.Namespace, db: PortfolioDB) -> None:
    if not db.holdings:
        print("아직 등록된 자산이 없습니다.")
        return

    print("\n[보유 자산 목록]")
    for h in db.holdings:
        print(
            f"- {h.market}:{h.symbol} ({h.asset_type}) | 수량 {h.quantity} | "
            f"평균매수 {format_money(h.avg_buy_price)} {h.currency} | "
            f"현재가 {format_money(h.current_price)} {h.currency} | "
            f"평가손익 {format_money(h.profit_loss)} {h.currency} ({h.profit_loss_rate:.2f}%)"
        )

    print("\n[통화별 요약]")
    for currency, stats in db.summary_by_currency().items():
        invested = stats["invested"]
        current = stats["current"]
        pnl = stats["profit_loss"]
        rate = (pnl / invested * 100) if invested else 0.0
        print(
            f"- {currency}: 투자원금 {format_money(invested)} | "
            f"평가금액 {format_money(current)} | "
            f"손익 {format_money(pnl)} ({rate:.2f}%)"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ETF/주식 포트폴리오 관리 CLI")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="포트폴리오 JSON 파일 경로")

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="자산 추가")
    add.add_argument("--symbol", required=True)
    add.add_argument("--market", required=True, help="국내(KR) 또는 국외(US) 등")
    add.add_argument("--asset-type", required=True, choices=["ETF", "STOCK", "etf", "stock"])
    add.add_argument("--quantity", required=True, type=float)
    add.add_argument("--avg-buy-price", required=True, type=float)
    add.add_argument("--current-price", required=True, type=float)
    add.add_argument("--currency", required=True, help="KRW, USD 등")

    update = sub.add_parser("update-price", help="현재가 업데이트")
    update.add_argument("--symbol", required=True)
    update.add_argument("--market", required=True)
    update.add_argument("--current-price", required=True, type=float)

    sub.add_parser("list", help="자산/요약 보기")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    db = PortfolioDB(args.db)

    if args.command == "add":
        cmd_add(args, db)
    elif args.command == "update-price":
        cmd_update(args, db)
    elif args.command == "list":
        cmd_list(args, db)


if __name__ == "__main__":
    main()
