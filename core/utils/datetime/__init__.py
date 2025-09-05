from datetime import datetime, timezone
import random
import re
import string

import pytz


class DatetimeUtils:
    @staticmethod
    def get_utc_now():
        return datetime.now(timezone.utc)

    @staticmethod
    def get_ist_now():
        """Get current datetime in IST timezone"""
        ist_timezone = pytz.timezone("Asia/Kolkata")
        return datetime.now(ist_timezone)
