from gws_core import Event, EventListener, event_listener


@event_listener
class GwsCoreDbListener(EventListener):
    """
    Listen to gws_core event to sync user database.

    Args:
        EventListener (_type_): _description_
    """

    def handle(self, event: Event) -> None:
        pass
        # if event.type == 'system' and event.action == 'started':
