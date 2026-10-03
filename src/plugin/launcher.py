from pyflowlauncher import FlowLauncherV2

# Reply that tells Flow Launcher to keep its window open after an action.
KEEP_OPEN = {"hide": False}


class HassLauncher(FlowLauncherV2):
    """FlowLauncherV2 with two gaps in pyflowlauncher 1.2.1 filled in.

    * A python_v2 host ignores ``DontHideAfterAction`` and hides the window
      unless the action replies ``{"hide": false}``, but pyflowlauncher always
      replies ``{"hide": true}``. Methods return ``KEEP_OPEN`` to stay open.
    * Query handlers only receive ``Query.search``. The action keyword the
      user typed is kept here so ``change_query`` can rebuild the full query.
    """

    def __init__(self) -> None:
        super().__init__()
        self.action_keyword = ""
        messages = self._client.messages

        async def track_action_keyword():
            async for request in messages():
                params = request.get("params") or []
                if request.get("method") == "query" and params and isinstance(params[0], dict):
                    self.action_keyword = params[0].get("actionKeyword") or ""
                yield request

        self._client.messages = track_action_keyword

    def _send_response(self, request_id, method, result):
        if result == KEEP_OPEN:
            self._respond(request_id, KEEP_OPEN)
        else:
            super()._send_response(request_id, method, result)
