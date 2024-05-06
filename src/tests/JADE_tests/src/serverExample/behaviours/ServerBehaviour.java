package serverExample.behaviours;


import jade.core.behaviours.SimpleBehaviour;
import jade.lang.acl.ACLMessage;

public class ServerBehaviour extends SimpleBehaviour {
    public void action() {
        String agentID = this.myAgent.getLocalName();
        System.out.println(agentID + ": ServerBehaviour action()");
        ACLMessage msg = this.myAgent.receive();
        if (msg != null) {
            int performativeNumber = msg.getPerformative();
            if (performativeNumber == 16) {
                String zenbakia = msg.getContent();
                System.out.println(msg.getSender().getLocalName() + "-tik " + zenbakia + " zenbakia jaso da");
                int num = Integer.parseInt(zenbakia);
                num *= num;
                String zenbakiBerri = String.valueOf(num);
                ACLMessage reply = msg.createReply();
                reply.setPerformative(7);
                reply.setContent(zenbakiBerri);
                this.myAgent.send(reply);
            } else if (performativeNumber == 7) {
                System.out.println(msg.getSender().getLocalName() + " agenteak ondo jaso du: " + msg.getContent());
            }
        } else {
            this.block();
        }

    }

    public boolean done() {
        String agentID = this.myAgent.getLocalName();
        System.out.println(agentID + ": ServerBehaviour done()");
        return false;
    }
}