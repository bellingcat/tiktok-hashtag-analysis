import os
import configparser
from pathlib import Path
import logging
from typing import Optional


class Authorization:
    """Handle authorization for TikTok, using the `msToken`."""

    def __init__(self, config_file: Optional[str] = None):
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = Path.home() / ".tiktok"

        self.section = "TikTok"
        self.ms_token = None

    def get_token(self) -> str:
        """Load the "msToken" cookie taken from TikTok, which the scraper requires."""

        # Step 1: check if MS_TOKEN is defined as environment variable
        if ms_token := os.environ.get("MS_TOKEN"):
            self.ms_token = ms_token
            logging.info("Loaded token from environment variable")

        # Step 2: check if MS_TOKEN is defined in config file
        elif self.config_file.is_file():
            if ms_token := self.load_token():
                self.ms_token = ms_token
                logging.info(f"Loaded token from config file: {self.config_file}")

        # Step 3: have user enter MS_TOKEN via terminal
        else:
            ms_token = self.input_token()
            self.dump_token(ms_token=ms_token)
            self.ms_token = ms_token
            logging.info(
                f"Loaded token from user input and saved to config file: {self.config_file}"
            )

        return self.ms_token

    def load_token(self) -> Optional[str]:
        """Parse a config file and extract the token."""

        config = configparser.ConfigParser()
        config.read(self.config_file)
        return config.get(section=self.section, option="MS_TOKEN", fallback=None)

    def dump_token(self, ms_token: str):
        """Write the token to a config file."""

        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.add_section(self.section)
        config.set(section=self.section, option="MS_TOKEN", value=ms_token)

        with open(self.config_file, "w", encoding="utf-8") as f:
            config.write(f)

    def input_token(self) -> str:
        """Allow user to manually enter the token in the terminal."""

        print(
            "\nPlease copy and paste your `msToken` cookie taken from your web browser when visiting the TikTok website. See [THIS VIDEO] for more information.\n"
        )

        ms_token = input("msToken: ")

        return ms_token
