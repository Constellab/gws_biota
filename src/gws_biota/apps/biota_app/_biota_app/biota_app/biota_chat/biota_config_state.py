from typing import cast

import reflex as rx
from gws_ai_toolkit._app.ai_chat import AppConfigState
from gws_biota.ai.biota_chat_config import BiotaChatConfig
from gws_core import Logger

from gws_reflex_main import ReflexMainState


class BiotaConfigState(rx.State):
    """State management for Biota chat configuration interface."""

    @rx.var
    async def show_settings_menu(self) -> bool:
        """Whether the settings menu should be shown in headers."""
        main_state = await self.get_state(ReflexMainState)
        return await main_state.get_param("show_config_page", False)

    async def get_config(self) -> BiotaChatConfig:
        app_config_state = await AppConfigState.get_instance(self)
        config = await app_config_state.get_config_section("biota_chat", BiotaChatConfig)
        return cast(BiotaChatConfig, config)

    @rx.var
    async def system_prompt(self) -> str:
        """Get the system prompt for the biota chat."""
        config = await self.get_config()
        return config.system_prompt

    @rx.var
    async def model(self) -> str:
        """Get the model for the biota chat."""
        config = await self.get_config()
        return config.model

    @rx.var
    async def temperature(self) -> float:
        """Get the temperature for the biota chat."""
        config = await self.get_config()
        return config.temperature

    @rx.var
    async def placeholder_text(self) -> str:
        """Get the placeholder text for the biota chat."""
        config = await self.get_config()
        return config.placeholder_text

    @rx.event
    async def handle_config_form_submit(self, form_data: dict):
        """Handle the configuration form submission."""
        try:
            new_system_prompt = form_data.get("system_prompt", "").strip()
            new_model = form_data.get("model", "").strip()
            new_temperature_str = form_data.get("temperature", "").strip()
            new_placeholder_text = form_data.get("placeholder_text", "").strip()

            if not new_system_prompt:
                return rx.toast.error("System prompt cannot be empty")

            if not new_model:
                return rx.toast.error("Model cannot be empty")

            if not new_placeholder_text:
                return rx.toast.error("Placeholder text cannot be empty")

            try:
                new_temperature = float(new_temperature_str)
                if new_temperature < 0.0 or new_temperature > 2.0:
                    return rx.toast.error("Temperature must be between 0.0 and 2.0")
            except ValueError:
                return rx.toast.error("Temperature must be a valid number")

            new_config = BiotaChatConfig(
                system_prompt=new_system_prompt,
                model=new_model,
                temperature=new_temperature,
                placeholder_text=new_placeholder_text,
            )

            app_config_state = await AppConfigState.get_instance(self)
            result = await app_config_state.update_config_section("biota_chat", new_config)

            if result:
                return rx.toast.success("Configuration updated successfully")

            return result

        except (ValueError, KeyError) as e:
            Logger.log_exception_stack_trace(e)
            return rx.toast.error(f"Configuration error: {e}")
        except Exception as e:
            Logger.log_exception_stack_trace(e)
            return rx.toast.error(f"Unexpected error updating configuration: {e}")
