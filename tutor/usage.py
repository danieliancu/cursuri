"""Înregistrarea consumului AI și calculul costurilor."""
from decimal import Decimal

from .models import ModelPrice, UsageRecord

MILLION = Decimal(1_000_000)


def price_for(model: str) -> ModelPrice | None:
    """Cel mai lung prefix care se potrivește (ex. „gpt-4.1” pentru „gpt-4.1-2025-04-14”)."""
    best = None
    for p in ModelPrice.objects.all():
        if model.startswith(p.model) and (best is None or len(p.model) > len(best.model)):
            best = p
    return best


def record(user, project: str, provider: str, model: str, *, input_tokens: int = 0, output_tokens: int = 0,
           cache_read_tokens: int = 0, cache_write_tokens: int = 0) -> UsageRecord:
    """Salvează un apel. `input_tokens` = tokeni de input facturați la preț întreg (fără cache)."""
    price = price_for(model)
    cost = Decimal(0)
    if price:
        cost = (
            input_tokens * price.input_usd
            + output_tokens * price.output_usd
            + cache_read_tokens * price.cache_read_usd
            + cache_write_tokens * price.cache_write_usd
        ) / MILLION
    return UsageRecord.objects.create(
        user=user,
        project=project,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_write_tokens=cache_write_tokens,
        cost_usd=cost,
        priced=price is not None,
    )
