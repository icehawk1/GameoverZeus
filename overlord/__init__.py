"""The overlord package contains two modules named Overlord and Host. The Overlord module manages a list of Mininet hosts that
each run one instance of the Host script. It is able to send RPC requests to those Host scripts. The RPC requests contain commands
to start or stop certain runnables. The Overlord module also contains functionality to infect and desinfect Bots, which means that
the runnable that executes botnet code is stopped and a victim runnable is started or vice versa.
The Host module is a Python script that can be executed on a Mininet host. It runs an RPC server and receives the start/stop
requests from the Overlord. The Host script also loads a common Twisted reactor that is shared by all runnables, because a reactor
is a Singleton for the whole process and can not be restarted, so it is not possible to have one reactor per thread or per runnable.
There should be only one Overlord per Experiment but many Hosts."""
