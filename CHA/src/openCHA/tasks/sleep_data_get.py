from typing import Any, Dict, List
import os

from openCHA.tasks import BaseTask
from pydantic import ConfigDict, PrivateAttr, field_validator


class SleepDataLookup(BaseTask):
    """
    **Description**

        Given a participant `id`, load *{id}_additional_sleep_data.csv* from
        /home/gdfwj/AIagant/data/DS8_SleepActivity/additional_sleep_data
        and return **all** sleep records as a list of dictionaries.
    """

    # ---------------------------------------------------------------------
    # OpenCHA metadata
    # ---------------------------------------------------------------------
    name: str = "sleep_data_lookup"
    chat_name: str = "SleepDataLookup"
    description: str = "Return all sleep records for the given participant id."
    dependencies: List[str] = []
    inputs: List[str] = ["Participant id (str or int)"]
    outputs: List[str] = [
        "A list of dictionaries, each representing one row of the user's "
        "sleep CSV. Example: [ {'sleep_id': '37190352839', 'start_time': "
        "'2022-06-08 00:45:30+02:00', ...}, ... ]"
    ]
    using_example: str = (
        "result = self.execute_task('sleep_data_lookup', ['001'])"
    )

    # ---------------------------------------------------------------------
    # Configuration & public fields
    # ---------------------------------------------------------------------
    model_config = ConfigDict(arbitrary_types_allowed=True)
    base_path: str = (
        "/home/gdfwj/AIagant/data/DS8_SleepActivity/additional_sleep_data"
    )

    # ---------------------------------------------------------------------
    # Private cache: {id: DataFrame}
    # ---------------------------------------------------------------------
    _cache: Any = PrivateAttr(default_factory=dict)

    # ---------------------------------------------------------------------
    # Validators
    # ---------------------------------------------------------------------
    @field_validator("base_path")
    def _check_base_path(cls, v: str) -> str:
        if not os.path.isdir(v):
            raise ValueError(f"Sleep data directory '{v}' does not exist.")
        # Verify pandas is available here as well
        try:
            import pandas as pd  # noqa: F401
        except ImportError as e:
            raise ValueError(
                "Could not import pandas. Please install it with `pip install pandas`."
            ) from e
        return v

    # ---------------------------------------------------------------------
    # Core execution
    # ---------------------------------------------------------------------
    def _execute(self, inputs: List[Any] | None = None) -> List[Dict[str, Any]]:
        if not inputs:
            raise ValueError("No id provided to SleepDataLookup task.")

        pid = str(inputs[0]).strip()

        # 1) 如果缓存里已有 DataFrame，直接用
        if pid in self._cache:
            df = self._cache[pid]
        else:
            # 2) 否则尝试读取文件并放入缓存
            import pandas as pd
            filename = f"{pid}_additional_sleep_data.csv"
            filepath = os.path.join(self.base_path, filename)

            if not os.path.isfile(filepath):
                raise ValueError(f"Sleep file '{filename}' not found.")

            df = pd.read_csv(filepath, dtype=str)
            self._cache[pid] = df

        # 3) 返回所有行转成 list[dict]
        return df.to_dict("records")

    # ---------------------------------------------------------------------
    # Human-readable explanation
    # ---------------------------------------------------------------------
    def explain(self) -> str:
        return (
            "Loads an individual's sleep CSV on demand, caches the DataFrame "
            "to avoid repeated disk reads, and returns all rows as a list of "
            "JSON-serialisable dictionaries."
        )
