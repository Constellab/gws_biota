# Plan: Biota Agent AI + Reflex Chat App

## Context

The goal is to create a simple Reflex chat app where users can ask questions about the Biota biological database (enzymes, compounds, reactions, pathways, taxonomy). The app uses an AI agent that wraps the 4 MCP biota v3 SQL tools as OpenAI function-calling tools, following the same `PlotlyAgentAi` pattern from `gws_ai_toolkit`.

Two deliverables:
1. **BiotaAgentAi** - agent class with 4 tools (get_schema, query, export_to_csv, database_statistics)
2. **Biota Reflex Chat App** - simple single-page chat UI at the existing biota_app skeleton

## File Structure

```
gws_biota/
  settings.json                                          # MODIFY: add gws_ai_toolkit dep
  src/gws_biota/
    ai/                                                  # NEW directory
      __init__.py                                        # NEW (empty)
      biota_db_tools.py                                  # NEW: DB functions from mcp_biota_v3
      biota_agent_ai_events.py                           # NEW: event types
      biota_agent_ai.py                                  # NEW: the agent class
    apps/biota_app/_biota_app/
      dev_config.json                                    # MODIFY: clean up params
      biota_app/
        biota_app.py                                     # REPLACE: new chat page
        biota_chat/                                      # NEW directory
          __init__.py                                    # NEW (empty)
          biota_chat_conversation.py                     # NEW: conversation bridge
          biota_chat_state.py                            # NEW: Reflex state
          biota_chat_component.py                        # NEW: UI component
```

## Step 1: Add gws_ai_toolkit dependency

**File:** `bricks/gws_biota/settings.json`

Add `gws_ai_toolkit` to the `environment.bricks` array:
```json
{"name": "gws_ai_toolkit", "version": "0.1.14"}
```

## Step 2: Create `gws_biota/ai/biota_db_tools.py`

Extract the pure database functions from `_ask_biota/mcp_biota_v3.py` (no MCP dependency):

- `DATABASE_SCHEMA` constant (the ~340-line markdown schema string, copy from mcp_biota_v3.py lines 114-340)
- `_get_db()` -> returns `BiotaDbManager.db`
- `_validate_readonly(sql)` -> security validation
- `_execute_sql(sql, limit)` -> execute SQL, return list of dicts
- `_enforce_max_limit(sql, max_limit)` -> cap LIMIT clause
- `get_schema() -> str` -> returns DATABASE_SCHEMA
- `query(sql, limit=10) -> dict` -> execute SELECT, max 20 rows
- `export_to_csv(sql, filename=None) -> dict` -> export to CSV at `/lab/user/data/`
- `get_database_statistics() -> dict` -> use raw SQL `SELECT COUNT(*) FROM table_name` for each entity table

**Key:** Use raw SQL counts for statistics (avoid importing all ORM models). Tables to count: `biota_enzymes`, `biota_protein`, `biota_compound`, `biota_reaction`, `biota_taxonomy`, `biota_pathways`, `biota_go`, `biota_bto`.

**Reuse from:** `/lab/user/bricks/gws_biota/_ask_biota/mcp_biota_v3.py` (lines 47-108 for helpers, 114-340 for schema, 500-538 for query, 546-601 for export_to_csv)

## Step 3: Create `gws_biota/ai/biota_agent_ai_events.py`

Define event types following `plotly_agent_ai_events.py` pattern:

- `SchemaResultEvent(FunctionSuccessEvent)` - type="schema_result", schema_text: str
- `QueryResultEvent(FunctionSuccessEvent)` - type="query_result", query_data: dict
- `ExportResultEvent(FunctionSuccessEvent)` - type="export_result", export_data: dict
- `StatisticsResultEvent(FunctionSuccessEvent)` - type="statistics_result", statistics_data: dict
- `BiotaAgentEvent` union type combining all above + `UserQueryTextEvent` + `BaseFunctionAgentEvent`

**Imports from:** `gws_ai_toolkit.core.agents.base_function_agent_events`

## Step 4: Create `gws_biota/ai/biota_agent_ai.py`

The main agent class extending `BaseFunctionAgentAi[BiotaAgentEvent, UserQueryTextEvent]`:

- **Pydantic configs:** `QueryConfig(BaseModelDTO)` with `sql: str`, `limit: int = 10`; `ExportToCsvConfig(BaseModelDTO)` with `sql: str`, `filename: str | None = None`
- **`_get_tools()`** - 4 tool defs in OpenAI function-calling format. `get_schema` and `get_database_statistics` have empty parameters. `query` and `export_to_csv` use `.model_json_schema()` from their config classes.
- **`_handle_function_call()`** - dispatch by `function_call_event.function_name`, call corresponding function from `biota_db_tools.py`, yield appropriate success event. For `function_response`, use `json.dumps(result, default=str)` for dict results, raw string for schema.
- **`_get_ai_instruction()`** - system prompt adapted from `_ask_biota/system_prompt_v3.md`: biological database expert, workflow (get_schema first, write SQL), key rules, follow-up suggestions, export offer.

**Pattern from:** `/lab/user/bricks/gws_ai_toolkit/src/gws_ai_toolkit/core/agents/table/plotly_agent_ai.py`
**Base class from:** `/lab/user/bricks/gws_ai_toolkit/src/gws_ai_toolkit/core/agents/base_function_agent_ai.py`

## Step 5: Create `biota_chat/biota_chat_conversation.py`

Bridge agent events to chat messages, extending `BaseChatConversation[ChatUserMessageText]`:

- **Constructor:** takes `BaseChatConversationConfig` + `BiotaAgentAi`, calls `super().__init__(config, mode="biota_agent", chat_configuration={...})`
- **`_call_ai_chat(user_message)`:** creates `UserQueryTextEvent`, iterates `biota_agent.call_agent(user_query)`, converts events to chat messages
- **Event handling:** `text_delta` -> `build_current_message()`, `response_created` -> store response_id, `response_completed` -> `close_current_message()`, `error`/`function_error` -> `ChatMessageError`. Function success events silently consumed (the base loop feeds them back to OpenAI).

**Pattern from:** `gws_ai_toolkit.models.chat.conversation.ai_table_agent_chat_conversation` (AiTableAgentChatConversation)
**Base class from:** `gws_ai_toolkit.models.chat.conversation.base_chat_conversation` (BaseChatConversation, BaseChatConversationConfig)

## Step 6: Create `biota_chat/biota_chat_state.py`

Reflex state extending `ConversationChatStateBase` (mixin) + `rx.State`:

- **UI config:** title="Biota Database Explorer", placeholder_text="Ask about enzymes, compounds, reactions...", empty_state_message="Ask me anything about the Biota biological database"
- **`_create_conversation()`:** reads API key from `os.getenv("OPENAI_API_KEY")`, creates `BiotaAgentAi(api_key, model="gpt-4o", temperature=0.3)`, creates `BaseChatConversationConfig("biota_agent", store_conversation_in_db=False, user=...)`, returns `BiotaChatConversation(config, biota_agent)`

**Import `ConversationChatStateBase` from:** `gws_ai_toolkit._app.ai_chat`
**Pattern from:** `ai_table_agent_chat_state.py`

## Step 7: Create `biota_chat/biota_chat_component.py`

Minimal component that wires `ChatConfig(state=BiotaChatState)` to `chat_component()`:

```python
from gws_ai_toolkit._app.ai_chat import ChatConfig, chat_component
from .biota_chat_state import BiotaChatState

def biota_chat_component() -> rx.Component:
    return chat_component(ChatConfig(state=BiotaChatState))
```

**Imports from:** `gws_ai_toolkit._app.ai_chat` (ChatConfig, chat_component)

## Step 8: Update `biota_app/biota_app.py`

Replace the template app with a single chat page:

```python
import reflex as rx
from gws_reflex_main import main_component, register_gws_reflex_app
from .biota_chat.biota_chat_component import biota_chat_component

app = register_gws_reflex_app()

@rx.page()
def index():
    return main_component(biota_chat_component())
```

## Step 9: Update `dev_config.json`

Clean up the template params:
```json
{
    "app_dir_path": "",
    "source_ids": [],
    "params": {},
    "env_type": "NONE",
    "env_file_path": "",
    "is_reflex_enterprise": false,
    "is_streamlit_v2": false,
    "dev_user_email": ""
}
```

## Streaming Data Flow

```
User types message in chat UI
  -> ConversationChatStateBase.submit_input_form()
    -> BiotaChatState._create_conversation() [lazy, first message only]
      -> BiotaAgentAi(api_key, model, temperature)
      -> BiotaChatConversation(config, agent)
    -> conversation.call_conversation(user_message)
      -> BiotaChatConversation._call_ai_chat()
        -> biota_agent.call_agent(UserQueryTextEvent)
          -> OpenAI streaming response
          -> Agent may call get_schema, query, etc.
          -> Function results fed back to OpenAI
          -> OpenAI generates text_delta events with summary
        -> text_delta -> build_current_message() -> ChatMessageStreaming
        -> response_completed -> close_current_message() -> ChatMessageText
    -> ChatMessageStreaming -> update UI in real-time
    -> ChatMessageText -> append to chat history
```

## Verification

1. **Run the app:**
   ```bash
   cd /lab/user/bricks/gws_biota/src/gws_biota/apps/biota_app/_biota_app
   gws reflex run dev_config.json
   ```
2. **Test the chat:** Type "What's in this database?" - agent should call `get_schema`, then respond with a summary
3. **Test a query:** Ask "How many enzymes are in the database?" - agent should call `query` with a COUNT SQL
4. **Test export:** Ask "Export all compounds to CSV" - agent should call `export_to_csv`
5. **Verify streaming:** Text should appear progressively, not all at once
6. **Verify error handling:** Submit an empty message (should be ignored), ask an impossible query (should show error gracefully)
