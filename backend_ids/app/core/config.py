# backend_ids/app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Paths
    ZEEK_DATA_DIR: str = Field("/home/server-ubuntu/zeek_flow/data", env="ZEEK_DATA_DIR")
    MODEL_DIR: str = Field("/home/server-ubuntu/zeek_flow/model", env="MODEL_DIR")
    
    # Files
    LIVE_STATE_FILE: str = Field("live_state.json", env="LIVE_STATE_FILE")
    CONN_LOG_FILE: str = Field("conn.log", env="CONN_LOG_FILE")
    DEFENSE_LOG_FILE: str = Field("defense_mode.log", env="DEFENSE_LOG_FILE")
    
    # Iptables
    IPTABLES_CHAIN: str = Field("FORWARD", env="IPTABLES_CHAIN")
    
    # API
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    DEBUG: bool = Field(False, env="DEBUG")
    
    @property
    def live_state_path(self) -> str:
        return f"{self.ZEEK_DATA_DIR}/{self.LIVE_STATE_FILE}"
    
    @property
    def conn_log_path(self) -> str:
        return f"{self.ZEEK_DATA_DIR}/{self.CONN_LOG_FILE}"
    
    @property
    def defense_log_path(self) -> str:
        return f"{self.ZEEK_DATA_DIR}/{self.DEFENSE_LOG_FILE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
