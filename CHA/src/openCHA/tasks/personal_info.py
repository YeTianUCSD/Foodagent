from typing import Any, Dict, List

import os
from openCHA.tasks import BaseTask
from pydantic import model_validator
import pandas as pd

class ParticipantInfoLookup(BaseTask):
    """
    **Description**

        Look up a participant's demographic and anthropometric information
        (age, sex, height, weight, intervention kcal, etc.) by `id`
        from *./data/participant_information.csv*.

    """

    # ---- Metadata required by OpenCHA -------------------------------------------------
    name: str = "participant_information_lookup"
    chat_name: str = "ParticipantInfoLookup"
    description: str = (
        "Given a participant `id`, return their basic information. "
    )
    dependencies: List[str] = []
    inputs: List[str] = ["A single string or int representing the participant id."]
    outputs: List[str] = [
        "Returns a JSON object with all columns for that participant. "
        "Example: {'id': '001', 'group': 'control', 'age': 34, ... }"
    ]
    using_example: str = (
        "result = self.execute_task('participant_information_lookup', ['001'])"
    )

    # ---- Internal attributes ----------------------------------------------------------
    csv_path: str = "/home/foodagent/code/Agent4Health/data/participant_information.csv"
    _df: Any = pd.read_csv(csv_path, dtype=str)  # populated in validator

    #csv_path: str = "/home/foodagent/code/Agent4Health/data/participant_information.csv"
    #_df: Any = None  


    # ---- Environment / dependency validation -----------------------------------------
    @model_validator(mode="before")
    def _validate_environment(cls, values: Dict) -> Dict:
        """
        Ensures `pandas` is installed and the CSV file exists, then pre-loads it.
        """
        values["csv_path"] = "/home/foodagent/code/Agent4Health/data/participant_information.csv"
        try:
            import pandas as pd  # noqa: F401
        except ImportError as e:
            raise ValueError(
                "Could not import pandas. Please install it with `pip install pandas`."
            ) from e

        if not os.path.exists(values.get("csv_path", "")):
            raise ValueError(
                f"{values.get('csv_path')} not found. "
                "Make sure the participant information CSV is in place."
            )

        # Load once and cache
        values["_df"] = pd.read_csv(values["csv_path"], dtype=str)
        return values

    # ---- Core execution logic ---------------------------------------------------------
    def _execute(self, inputs: List[Any] = None) -> Dict[str, Any]:
        """
        Parameters
        ----------
        inputs : List[Any]
            inputs[0] – participant id (str or int)

        Returns
        -------
        Dict[str, Any]
            A JSON-serialisable dict of the participant’s row in the CSV.

        Raises
        ------
        ValueError
            If the id is missing or not found in the file.
        """
        if not inputs:
            raise ValueError("No id provided to ParticipantInfoLookup task.")

        participant_id = str(inputs[0]).strip()

        match = self._df[self._df["id"] == participant_id]
        if match.empty:
            raise ValueError(f"Participant id '{participant_id}' not found.")

        # `to_dict('records')[0]` returns a plain dict for the first (and only) row
        return match.to_dict("records")[0]

    # ---- Human-readable explanation ---------------------------------------------------
    def explain(self) -> str:
        return (
            "This task loads '/home/foodagent/code/Agent4Health/data/participant_information.csv' once at "
            "startup, then filters the DataFrame by the provided `id` and "
            "returns the matched row as a JSON object."
        )
