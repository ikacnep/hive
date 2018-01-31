class ActionResult:

    def __init__(self):
        self.result = True
        self.reason = None
        self.message = None
        self.state = None
        self.actions = None

    def FillJson(self, rv):
        rv["result"] = self.result
        if self.reason is not None:
            rv["reason"] = self.reason
        if self.message is not None:
            rv["message"] = self.message
        if self.state is not None:
            rv["state"] = self.state.GetJson()
        if self.actions is not None:
            rv["actions"] = self.actions.GetJson()
