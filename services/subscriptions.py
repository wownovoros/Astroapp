from database.db import subscription_is_active


def has_active_subscription(user_row) -> bool:
    return subscription_is_active(user_row)
