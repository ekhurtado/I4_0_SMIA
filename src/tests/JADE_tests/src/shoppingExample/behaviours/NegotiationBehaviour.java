package shoppingExample.behaviours;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.SimpleBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.io.IOException;

public class NegotiationBehaviour extends SimpleBehaviour {

    private long myValue;
    private String[] targets;
    private String negotiationCriteria;
    private String conversationID;
    private String sender;
    private MessageTemplate messageTemplate;
    private int step = 0;
    private int repliesCnt;

    public NegotiationBehaviour(Agent agent, String targets, String negotiationCriteria, String conversationID, String sender){
        super(agent);
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": params " + targets + ", " + negotiationCriteria + ", " + conversationID);
        this.targets = targets.split(",");
        if(negotiationCriteria.contains("max")) {
            this.negotiationCriteria = "max";
        } else if(negotiationCriteria.contains("min")) {
            this. negotiationCriteria = "min";
        }
        this.conversationID=conversationID;
        this.sender = sender;
        repliesCnt=0;
    }

    public void onStart(){
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": NegotiationBehaviour onStart()");

        myValue = freeMemory();
        System.out.println(agentID + ": freeMemory " + myValue);

        MessageTemplate matchPerformative = MessageTemplate.MatchPerformative(ACLMessage.PROPOSE);
        MessageTemplate matchOntology = MessageTemplate.MatchOntology("negotiation");
        MessageTemplate matchConversationID = MessageTemplate.MatchConversationId(conversationID);
        messageTemplate = MessageTemplate.and((MessageTemplate.and(matchOntology, matchPerformative)), matchConversationID);
        System.out.println(agentID + ": configured message template for PROPOSE performative");
    }

    @Override
    public void action() {
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": NegotiationBehaviour action()");

        switch(step) {
            case 0:
                System.out.println(agentID + ": NegotiationBehaviour case 0");
                ACLMessage proposeMsg = new ACLMessage(ACLMessage.PROPOSE);
                proposeMsg.setOntology("negotiation");
                proposeMsg.setConversationId(conversationID);
                for(String nodeAgentID : targets) {
                    if(!nodeAgentID.equals(agentID)) {
                        proposeMsg.addReceiver(new AID(nodeAgentID, AID.ISLOCALNAME));
                        try {
                            proposeMsg.setContentObject(myValue);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        myAgent.send(proposeMsg);
                        System.out.println(agentID + ": sending message to " + nodeAgentID);
                    }
                }

                step = 1;
                break;

            case 1:
                System.out.println(agentID + ": NegotiationBehaviour case 1");

                ACLMessage replyMsg = myAgent.receive(messageTemplate);
                if(replyMsg != null) {
                    if(replyMsg.getPerformative() == ACLMessage.PROPOSE) {
                        AID senderResource = replyMsg.getSender();
                        System.out.println(agentID + ": received message from " + senderResource.getLocalName());

                        long receivedValue = 0;
                        try {
                            receivedValue = (long) replyMsg.getContentObject();
                            System.out.println(agentID + ": received value " + receivedValue);
                        } catch(Exception e) {
                            e.printStackTrace();
                        }

                        receivedValue = (negotiationCriteria.equals("max") ? receivedValue : -receivedValue);
                        if(receivedValue > myValue) {
                            step = 3;
                        }
                    }

                    repliesCnt++;
                    if(repliesCnt >= targets.length-1) {
                        step = (step == 3) ? 3 : 2;
                        break;
                    }
                } else {
                    block();
                }
                break;

            case 2:
                System.out.println(agentID + ": NegotiationBehaviour case 2");

                ACLMessage informMsg = new ACLMessage(ACLMessage.INFORM);
                informMsg.addReceiver(new AID(this.sender, AID.ISLOCALNAME));
                informMsg.setOntology("negotiation");
                informMsg.setConversationId(conversationID);
                informMsg.setContent("winner=" + myAgent.getLocalName());
                myAgent.send(informMsg);
                System.out.println(agentID + ": sending message to " + sender);

                step = 4;
                break;

            case 3:
                System.out.println(agentID + ": NegotiationBehaviour case 3");
                step = 4;
                break;

            default:
                break;
        }
    }

    @Override
    public boolean done() {
        String agentID = myAgent.getLocalName();
        System.out.println(agentID + ": NegotiationBehaviour done()");

        return (step == 4);
    }

    protected long freeMemory() {
        Runtime rt;
        rt = Runtime.getRuntime();
        long maxMem = rt.maxMemory();
        long totalMem = rt.totalMemory();
        long freeMem = rt.freeMemory();
        long effectiveFreeMem = maxMem - (totalMem - freeMem);
        return effectiveFreeMem;
    }
}
