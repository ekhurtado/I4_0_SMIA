package shoppingExample;

import jade.core.Agent;
import jade.core.behaviours.SimpleBehaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;

import shoppingExample.behaviours.RunningBehaviour;

public class ResourceAgent extends Agent {

    @Override
    protected void setup() {
        String agentID = this.getLocalName();
        System.out.println(agentID + ": ResourceAgent setup()");

        ServiceDescription sd = new ServiceDescription();
        sd.setName("skill");
        String skill = this.getArguments()[0].toString();
        System.out.println(agentID + ": skill " + skill);
        sd.setType(skill);
        DFAgentDescription dfad = new DFAgentDescription();
        dfad.addServices(sd);
        try{
            DFService.register(this, dfad);
        } catch(FIPAException e) {
            e.printStackTrace();
        }

        SimpleBehaviour runningBehaviour = new RunningBehaviour(this);
        addBehaviour(runningBehaviour);
    }

    @Override
    public void doDelete() {
        // perform the before die tasks
        System.out.println("Executing doDelete");
    }
}
