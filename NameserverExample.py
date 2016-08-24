#!/usr/bin/env python2
# coding=UTF-8
import logging, time
from resources.emu_config import logging_config
from Experiment import Experiment


class NameserverExperiment(Experiment):
    def _setup(self):
        super(NameserverExperiment, self)._setup()
        self.setNodes("bots", {self.addHostToMininet(self.switch, "bot%d"%i) for i in range(5)})
        self.setNodes("cncservers", {self.addHostToMininet(self.switch, "cnc%d"%i) for i in range(3)})
        self.setNodes("nameserver", {self.addHostToMininet(self.switch, "ns1")})

    def _start(self):
        super(NameserverExperiment, self)._start()
        nameserver = next(iter(self.getNodes("nameserver")))

        # Start the necessary runnables
        self.overlord.startRunnable("nameserver", "Nameserver", kwargs={"peerlist": [h.IP() for h in self.getNodes("cncserver")]},
                                    hostlist=[nameserver.name])
        self.overlord.startRunnable("zeus.CnCServer", "CnCServer", hostlist=[h.name for h in self.getNodes("cncserver")])
        for h in self.getNodes("bots"):
            self.overlord.startRunnable("zeus.Bot", "Bot", hostlist=[h.name],
                                        kwargs={"name": h.name, "peerlist": [nameserver.IP()], "pauseBetweenDuties": 1})

    def _executeStep(self, num):
        super(NameserverExperiment, self)._executeStep(num)
        time.sleep(50)
        return False

    def _stop(self):
        super(NameserverExperiment, self)._stop()

    def _produceOutputFiles(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    experiment = NameserverExperiment()
    experiment.executeExperiment()
