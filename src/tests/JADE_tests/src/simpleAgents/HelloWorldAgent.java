package simpleAgents;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;

public class HelloWorldAgent extends Agent {

    protected void setup() {
        System.out.println("Hello World! My name is "+getLocalName());

        // Make this agent terminate
//        doDelete();

    }


}

