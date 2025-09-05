from datetime import datetime
import io
import traceback
from concurrent.futures import ThreadPoolExecutor
import requests
import pytz


class DiscordLogger:
    executor = ThreadPoolExecutor()
    LOG_CHANNELS = {}

    @classmethod
    def register_log_channel(cls, name: str, webhook_url: str):
        cls.LOG_CHANNELS[name] = webhook_url

    def get_ist_timestamp(self, cls) -> str:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        return datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")

    def parse_exception_with_traceback(self, exception: Exception) -> str:
        """Parse exception with traceback details."""
        error_type = type(exception).__name__
        error_message = str(exception)
        tb_details = "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )
        return f"Error Type: {error_type}\nError Message: {error_message}\n\nTraceback:\n{tb_details}"

    def send_log(
        self,
        message: str,
        channel: str = "log",
        synchronous: bool = False,
        raise_on_error: bool = True,
    ):
        """Send log message  in discord."""
        if not self.LOG_CHANNELS.get(channel):
            if raise_on_error:
                raise ValueError(
                    f"The channel '{channel}' is not registered. Please register it using register_log_channel."
                )
            else:
                print(
                    f"The channel '{channel}' is not registered. Please register it using register_log_channel."
                )
                return

        payload = {
            "content": f"{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %I:%M %p')} (IST) {message}"
        }

        def task():
            try:
                response = requests.post(self.LOG_CHANNELS["log"], data=payload)
                if response.status_code != 204:
                    print(
                        f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                print(f"Error sending Discord notification: {str(e)}")

        if synchronous:
            task()
        else:
            self.executor.submit(task)

    def send_error_alert(
        self,
        exception: Exception,
        track_id: str,
        channel: str = "alert",
        synchronous: bool = False,
        raise_on_error: bool = True,
    ):
        """Send error details to a Discord channel in a background task."""
        if not self.LOG_CHANNELS.get(channel):
            if raise_on_error:
                raise ValueError(
                    f"The channel '{channel}' is not registered. Please register it using register_log_channel."
                )
            else:
                print(
                    f"The channel '{channel}' is not registered. Please register it using register_log_channel."
                )
                return

        error_details = self.parse_exception_with_traceback(exception)
        timestamp = self.get_ist_timestamp()
        error_filename = f"error_{track_id}.txt"
        memory_file = io.BytesIO()
        memory_file.write(
            f"Error Code: {track_id}\nTimestamp (IST): {timestamp}\n\n{error_details}".encode()
        )
        memory_file.seek(0)
        payload = {"content": f""}
        files = {"file": (error_filename, memory_file)}

        def task():
            try:
                response = requests.post(
                    self.LOG_CHANNELS["alert"], data=payload, files=files
                )
                if response.status_code != 204:
                    print(
                        f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                print(f"Error sending Discord notification: {str(e)}")
            finally:
                memory_file.close()

        if synchronous:
            task()
        else:
            # Submit the background task
            self.executor.submit(task)


register_log_channel = DiscordLogger.register_log_channel
discord_logger = DiscordLogger()
