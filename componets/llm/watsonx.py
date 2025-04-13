from langflow.base.models.model import LCModelComponent
from langflow.field_typing import LanguageModel
from langchain_ibm import ChatWatsonx
from pydantic.v1 import SecretStr
from typing import Any, List

import requests

from langflow.inputs import DropdownInput, IntInput, SecretStrInput, StrInput, BoolInput, SliderInput
from langflow.field_typing.range_spec import RangeSpec
from langflow.schema.dotdict import dotdict

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatsonxComponent(LCModelComponent):
    """
    Component for interacting with the IBM watsonx.ai foundation models.

    This component allows users to generate text using various IBM watsonx.ai models.
    It provides configurable parameters for controlling the generation process,
    such as model selection, API endpoint, temperature, and maximum tokens.
    """

    display_name = "IBM watsonx.ai"
    description = "Generate text using IBM watsonx.ai foundation models."
    beta = False

    _default_models = ["ibm/granite-3-2b-instruct", "ibm/granite-3-8b-instruct", "ibm/granite-13b-instruct-v2"]

    inputs = [
        *LCModelComponent._base_inputs,
        DropdownInput(
            name="url",
            display_name="watsonx API Endpoint",
            info="The base URL of the API.",
            value=None,
            options=[
                "https://us-south.ml.cloud.ibm.com",
                "https://eu-de.ml.cloud.ibm.com",
                "https://eu-gb.ml.cloud.ibm.com",
                "https://au-syd.ml.cloud.ibm.com",
                "https://jp-tok.ml.cloud.ibm.com",
                "https://ca-tor.ml.cloud.ibm.com",
            ],
            real_time_refresh=True,
        ),
        StrInput(
            name="project_id",
            display_name="watsonx Project ID",
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="The API Key to use for authentication with the model.",
            required=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            options=[],
            value=None,
            dynamic=True,
            required=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="The maximum number of tokens to generate.",
            range_spec=RangeSpec(min=1, max=4096),
            value=1000,
        ),
        StrInput(
            name="stop_sequence",
            display_name="Stop Sequence",
            advanced=True,
            info="Sequence where generation should stop.",
            field_type="str",
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness, higher values increase diversity.",
            value=0.1,
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
        SliderInput(
            name="top_p",
            display_name="Top P",
            info="The cumulative probability cutoff for token selection. "
            "Lower values mean sampling from a smaller, more top-weighted nucleus.",
            value=0.9,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            advanced=True,
        ),
        SliderInput(
            name="frequency_penalty",
            display_name="Frequency Penalty",
            info="Penalty for frequency of token usage.",
            value=0.5,
            range_spec=RangeSpec(min=-2.0, max=2.0, step=0.01),
            advanced=True,
        ),
        SliderInput(
            name="presence_penalty",
            display_name="Presence Penalty",
            info="Penalty for token presence in prior text.",
            value=0.3,
            range_spec=RangeSpec(min=-2.0, max=2.0, step=0.01),
            advanced=True,
        ),
        IntInput(
            name="seed",
            display_name="Random Seed",
            advanced=True,
            info="The random seed for the model.",
            value=8,
        ),
        BoolInput(
            name="logprobs",
            display_name="Log Probabilities",
            advanced=True,
            info="Whether to return log probabilities of the output tokens.",
            value=True,
        ),
        IntInput(
            name="top_logprobs",
            display_name="Top Log Probabilities",
            advanced=True,
            info="Number of most likely tokens to return at each position.",
            value=3,
            range_spec=RangeSpec(min=1, max=20),
        ),
    ]

    @staticmethod
    def fetch_models(base_url: str) -> List[str]:
        """
        Fetch available foundation model IDs from the watsonx.ai API for a given base URL.

        This method makes a GET request to the watsonx.ai API endpoint to retrieve a list
        of available foundation models, filtering for 'function_text_chat' models that are
        not lifecycle withdrawn.

        Args:
            base_url (str): The base URL of the watsonx.ai API endpoint.

        Returns:
            List[str]: A sorted list of available model IDs.
                       Returns a list of default models if an error occurs during fetching.
        """
        try:
            endpoint = f"{base_url}/ml/v1/foundation_model_specs"
            params = {"version": "2024-09-16", "filters": "function_text_chat,!lifecycle_withdrawn"}
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            models = [model["model_id"] for model in data.get("resources", [])]
            return sorted(models)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching models from {base_url}: {e}")
            logger.info("Using default models.")
            return WatsonxComponent._default_models
        except ValueError as e:
            logger.error(f"Error decoding JSON response from {base_url}: {e}")
            logger.info("Using default models.")
            return WatsonxComponent._default_models
        except Exception as e:
            logger.exception(f"An unexpected error occurred while fetching models from {base_url}: {e}")
            logger.info("Using default models.")
            return WatsonxComponent._default_models

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None):
        """
        Update the build configuration, specifically the available model options,
        when the API endpoint URL changes.

        This method is triggered when the 'url' input field is modified. It fetches
        the available models for the new URL and updates the options for the 'model_name'
        dropdown input.

        Args:
            build_config (dotdict): The current build configuration dictionary.
            field_value (Any): The new value of the modified field.
            field_name (str | None): The name of the modified field (should be 'url').
        """
        logger.info(f"Updating build config. Field name: {field_name}, Field value: {field_value}")

        if field_name == "url" and field_value:
            try:
                models = self.fetch_models(base_url=build_config.url.value)
                build_config.model_name.options = models
                if build_config.model_name.value not in models and models:
                    build_config.model_name.value = models[0]  # Set to the first available model if the previous one is not found
                info_message = f"Updated model options: {len(models)} models found in {build_config.url.value}"
                logger.info(info_message)
            except Exception:
                logger.exception("Error updating model options.")

    def build_model(self) -> LanguageModel:
        """
        Build and return a ChatWatsonx language model instance based on the component's configuration.

        This method retrieves the configured parameters from the component's attributes
        and uses them to instantiate a `ChatWatsonx` object.

        Returns:
            LanguageModel: An instance of the `ChatWatsonx` class configured with the user-provided parameters.
        """
        chat_params = {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "stop": [self.stop_sequence] if self.stop_sequence else [],
            "n": 1,
            "logprobs": self.logprobs,
            "top_logprobs": self.top_logprobs,
            "time_limit": 600000,
            "logit_bias": {"1003": -100, "1004": -100},  # Example logit bias
        }

        return ChatWatsonx(
            apikey=SecretStr(self.api_key).get_secret_value(),
            url=self.url,
            project_id=self.project_id,
            model_id=self.model_name,
            params=chat_params,
            streaming=self.stream,
        )