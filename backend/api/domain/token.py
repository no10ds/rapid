from api.common.logger import AppLogger


class Token:
    def __init__(self, payload: dict):
        self.subject: str = self._extract_subject(payload)

    def _extract_subject(self, payload: dict) -> str:
        try:
            subject = payload["sub"]
        except KeyError:
            AppLogger.info("No subject field defined in the payload.")
            raise ValueError("No Subject key")

        if not subject:
            AppLogger.info("No value for subject in the payload.")
            raise ValueError("Invalid Subject field")

        return subject
