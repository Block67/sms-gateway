from pydantic_settings import BaseSettings, SettingsConfigDict


class QueueConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    RABBITMQ_URL: str = "amqp://guest:guest@localhost/"
    RABBITMQ_SMS_QUEUE: str = "sms_send_queue"
    SMS_SEND_INTERVAL_MS: int = 1000

    RABBITMQ_DLR_QUEUE: str = "dlr_forward_queue"
    DLR_FORWARD_MAX_RETRIES: int = 3
    DLR_FORWARD_RETRY_BACKOFF_SECONDS: float = 2.0


queue_config = QueueConfig()
