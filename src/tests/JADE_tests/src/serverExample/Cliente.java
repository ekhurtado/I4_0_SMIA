package serverExample;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.SimpleBehaviour;
import jade.domain.DFService;
import jade.domain.FIPAException;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.lang.acl.ACLMessage;
import serverExample.behaviours.ClientBehaviour;

import java.util.Arrays;

public class Cliente extends Agent {
    protected void setup() {
        try {
            Thread.sleep(1000L);
        } catch (Exception var6) {
        }

        String agentID = this.getLocalName();
        System.out.println(agentID + ": Cliente setup()");

//        System.out.println(Arrays.toString(this.getArguments()));
//        String num = this.getArguments()[0].toString();
        String num = "1"; // assigned the name directly for the tests

        System.out.println(agentID + " parameter: " + num);
        this.serviceRegister(num);
        SimpleBehaviour clienteBehaviour = new ClientBehaviour();
        this.addBehaviour(clienteBehaviour);

        // If it is in a Docker container it gets the server name from an environmental variable
//        String serverName = System.getenv("SERVER_NAME");
        String serverName = "servidor"; // assigned the name directly for the tests

        ACLMessage msg = new ACLMessage(16);
        msg.addReceiver(new AID(serverName, false));
        msg.setOntology("Numerical operation");
        msg.setContent(num);
        this.send(msg);
        System.out.println(agentID + " Mezua bidali dio zerbitzariari");
        System.out.println(agentID + ": Cliente exiting setup");
    }

    private void serviceRegister(String num) {
        ServiceDescription sd = new ServiceDescription();
        sd.setName("number");
        sd.setType(num);
        DFAgentDescription dfad = new DFAgentDescription();
        dfad.addServices(sd);

        try {
            DFService.register(this, dfad);
            System.out.println(this.getLocalName() + " registered");
        } catch (FIPAException var5) {
            var5.printStackTrace();
        }

    }

    private void serviceDeregister() {
        try {
            DFService.deregister(this);
            System.out.print(this.getLocalName() + "\t --> Agent services deregistered. ");
        } catch (FIPAException var2) {
            var2.printStackTrace();
        }

        System.out.println("Check agent registration in DF GUI");
    }

    protected void takeDown() {
        String agentID = this.getLocalName();
        System.out.println(agentID + ": Cliente takeDown()");
        this.serviceDeregister();
    }
}