package serverExample;

import jade.core.Agent;
import serverExample.behaviours.ServerBehaviour;

public class Servidor extends Agent {
    protected void setup() {
        try {
            Thread.sleep(1000L);
        } catch (Exception var3) {
        }

        String agentID = this.getLocalName();
        System.out.println(agentID + ": Servidor setup()");
        ServerBehaviour behaviour = new ServerBehaviour();
        this.addBehaviour(behaviour);
    }

    protected void takeDown() {
        String agentID = this.getLocalName();
        System.out.println(agentID + ": Servidor takeDown()");
    }
}