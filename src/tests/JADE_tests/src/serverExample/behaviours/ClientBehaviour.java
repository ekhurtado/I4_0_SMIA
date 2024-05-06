package serverExample.behaviours;

import jade.core.behaviours.SimpleBehaviour;
import jade.lang.acl.ACLMessage;

public class ClientBehaviour extends SimpleBehaviour {
    public void action() {
        String agentID = this.myAgent.getLocalName();
        System.out.println(agentID + ": ClientBehaviour action()");
        ACLMessage msg = this.myAgent.receive();
        if (msg != null) {
            String zenbakiZerbitzari = msg.getContent();
            System.out.println(msg.getSender().getLocalName() + " agenteak bueltatutako zenbakia: " + zenbakiZerbitzari);
            ACLMessage reply = msg.createReply();
            reply.setPerformative(7);
            reply.setContent("Zenbakia ondo jaso dut!");
            this.myAgent.send(reply);
        } else {
            this.block();
        }

    }

    public boolean done() {
        String agentID = this.myAgent.getLocalName();
        System.out.println(agentID + ": ClientBehaviour done()");
        return false;
    }
}