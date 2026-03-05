import reflex as rx

from .biota_config_state import BiotaConfigState


def biota_config_component() -> rx.Component:
    """Biota chat configuration interface component.

    Provides a form for configuring the system prompt, model, temperature,
    and placeholder text for the Biota chat agent.
    """
    return rx.vstack(
        rx.hstack(
            rx.heading("Biota Chat Configuration"),
            rx.spacer(),
            rx.button(
                rx.icon("x", size=16),
                variant="ghost",
                size="2",
                cursor="pointer",
                color="var(--gray-11)",
                on_click=rx.redirect("/"),
            ),
            align="center",
            width="100%",
        ),
        rx.vstack(
            rx.form(
                rx.vstack(
                    rx.heading("Model Configuration", size="4"),
                    rx.text("OpenAI model to use for AI responses:", color="gray"),
                    rx.input(
                        placeholder="Enter model name (e.g., gpt-4o, gpt-4o-mini)...",
                        name="model",
                        default_value=BiotaConfigState.model,
                        width="100%",
                    ),
                    rx.heading("Temperature", size="4", margin_top="4"),
                    rx.text("Controls randomness: 0.0 = focused, 2.0 = creative", color="gray"),
                    rx.input(
                        placeholder="0.3",
                        name="temperature",
                        default_value=rx.cond(
                            BiotaConfigState.temperature,
                            BiotaConfigState.temperature.to(str),
                            "0.3",
                        ),
                        type="number",
                        min=0.0,
                        max=2.0,
                        step=0.1,
                        width="100%",
                    ),
                    rx.heading("System prompt", size="4", margin_top="4"),
                    rx.text("Instructions for the AI agent:", color="gray"),
                    rx.text_area(
                        placeholder="Enter system prompt...",
                        name="system_prompt",
                        default_value=BiotaConfigState.system_prompt,
                        resize="vertical",
                        rows="15",
                        width="100%",
                    ),
                    rx.heading("Placeholder text", size="4", margin_top="4"),
                    rx.text("Text shown in the chat input field:", color="gray"),
                    rx.input(
                        placeholder="Ask about enzymes, compounds, reactions...",
                        name="placeholder_text",
                        default_value=BiotaConfigState.placeholder_text,
                        width="100%",
                    ),
                    rx.button("Update Configuration", type="submit"),
                    spacing="3",
                    width="100%",
                ),
                on_submit=BiotaConfigState.handle_config_form_submit,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="6",
        width="100%",
    )
