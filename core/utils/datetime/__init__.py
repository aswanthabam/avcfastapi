from datetime import datetime, timezone
import random
import re
import string


class DatetimeUtils:
    @staticmethod
    def get_utc_now():
        return datetime.now(timezone.utc)
