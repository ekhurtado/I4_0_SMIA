from spade.behaviour import OneShotBehaviour


class OperatorBehaviour(OneShotBehaviour):
    """The behavior for the Operator only needs to add the web interface to the SMIA SPADE agent and the GUI related
    resources (HTML web pages and drivers)."""

    async def run(self) -> None:
        # First, the web interface is enabled in the SMIA SPADE agent
        self.agent.web.start(hostname="0.0.0.0", port="10000")

        # Then, the required HTML webpages are added to the SMIA SPADE web module
        self.agent.add_get('/system_view', GUIControllers, '/htmls/send_acl.html')

        # TODO se ha añadido el Sen ACL del GUIAgent para realizar la prueba, hay que desarrollar los HTMLs para el
        #  operario y añadirlos

class GUIControllers:
    """This class contains all the controller to be added to SMIA in order to manage the operator actions."""

    @staticmethod
    async def hello_controller(request):
        print(request)
        return {"status": "OK"}