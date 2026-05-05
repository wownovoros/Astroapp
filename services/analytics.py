from database.db import get_conversion_stats, log_event


def track_event(user_id: int, event: str, metadata: str = "") -> None:
    log_event(user_id, event, metadata)


def format_stats() -> str:
    stats = get_conversion_stats()
    return (
        "Аналитика воронки:\n"
        f"start: {stats['start']}\n"
        f"birthdate_saved: {stats['birthdate_saved']}\n"
        f"view_horoscope: {stats['view_horoscope']}\n"
        f"paywall: {stats['paywall']}\n"
        f"paid: {stats['paid']}"
    )
