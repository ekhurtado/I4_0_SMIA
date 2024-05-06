package shoppingExample;

import java.util.List;
import java.util.ArrayList;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

public class BuyerAgent extends Agent {

    @Override
    protected void setup() {
        String agentID = this.getLocalName();
        System.out.println(agentID + ": BuyerAgent setup()");
        String skill = this.getArguments()[0].toString();
        String negotiationCriteria = this.getArguments()[1].toString();
        System.out.println(agentID + ": parameters " + skill + ", " + negotiationCriteria);

        ServiceDescription sd = new ServiceDescription();
        sd.setName("skill");
        sd.setType(skill);
        DFAgentDescription dfad = new DFAgentDescription();
        dfad.addServices(sd);
        DFAgentDescription[] availableResources = {};
        try {
            availableResources = DFService.search(this, dfad);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        List<String> resourceList = new ArrayList<String>();
        for(DFAgentDescription dfad_aux : availableResources) {
            resourceList.add(dfad_aux.getName().getLocalName());
        }
        String resourceListString = String.join(",", resourceList);

        String conversationID = String.valueOf(System.currentTimeMillis());
        for(DFAgentDescription dfad_aux : availableResources) {
            ACLMessage informMsg = new ACLMessage(ACLMessage.CFP);
            informMsg.addReceiver(dfad_aux.getName());
            informMsg.setOntology("negotiation");
            informMsg.setConversationId(conversationID);
            informMsg.setContent("resources=" + resourceListString + " negotiationCriteria=" + negotiationCriteria);
            System.out.println(agentID + ": message content: " + informMsg.getContent());
            this.send(informMsg);
            System.out.println(agentID + ": sending message to " + dfad_aux.getName().getLocalName());
        }

        MessageTemplate matchPerformative = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
        MessageTemplate matchOntology = MessageTemplate.MatchOntology("negotiation");
        MessageTemplate matchConversationID = MessageTemplate.MatchConversationId(conversationID);
        MessageTemplate messageTemplate = MessageTemplate.and((MessageTemplate.and(matchOntology, matchPerformative)), matchConversationID);

        ACLMessage informMsg;
        do {
            informMsg = this.receive(messageTemplate);
            if(informMsg != null) {
                if (informMsg.getPerformative() == ACLMessage.INFORM) {
                    String messageContent = informMsg.getContent();
                    System.out.println(agentID + ": " + messageContent);
                }
            }
        } while(informMsg == null);
    }

    @Override
    public void doDelete() {
        // perform the before die tasks
        System.out.println("Executing doDelete");
    }
}
