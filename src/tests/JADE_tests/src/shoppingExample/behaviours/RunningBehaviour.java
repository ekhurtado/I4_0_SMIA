package shoppingExample.behaviours;

import jade.core.Agent;
import jade.core.behaviours.SimpleBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

public class RunningBehaviour extends SimpleBehaviour {

    private MessageTemplate messageTemplate;

    public RunningBehaviour(Agent agent) {
        super(agent);
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": RunningBehaviour setup()");

        MessageTemplate matchOntology = MessageTemplate.MatchOntology("negotiation");
        MessageTemplate matchPerformative = MessageTemplate.MatchPerformative(ACLMessage.CFP);
        messageTemplate = MessageTemplate.and(matchOntology, matchPerformative);
        System.out.println(agentID + ": configured message template for CFP performative");
    }

    @Override
    public void action() {
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": RunningBehaviour action()");

        ACLMessage cfpMsg = myAgent.receive(messageTemplate);
        if(cfpMsg != null) {
            if(cfpMsg.getPerformative() == ACLMessage.CFP) {
                String[] messageContent = cfpMsg.getContent().split(" ");
                String[] targets = messageContent[0].split("=");
                String[] negotiationCriteria = messageContent[1].split("=");
                String conversationID = cfpMsg.getConversationId();
                String sender = cfpMsg.getSender().getLocalName();
                myAgent.addBehaviour(new NegotiationBehaviour(myAgent, targets[1], negotiationCriteria[1], conversationID, sender));
            }
        }  else {
           block();
        }
    }

    @Override
    public boolean done() {
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": RunningBehaviour done()");
        return false;
    }
}
