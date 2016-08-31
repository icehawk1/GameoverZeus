How to install and run the Botnet Emulator
=========================================
This document describes the files that can be found in the submission directory and how to run the software product that was developed for this thesis.

Contents of the submission directory
------------------------------------
This directory contains the text of the MSc thesis in the file Msc_project_2214231.pdf .
It also contains the directory BotnetEmulator where the implemented software is located.
The BotnetEmulator directory contains a number of Python scripts, most notably OverbotExperiment.py, ZeusExperiment.py, PerformanceExperiment.py and PingExperiment.py.
Those files implement the experiments described in the thesis.

Requirements
------------
The BotnetEmulator has been tested on Ubuntu Linux 15.10 and 14.04 and was implemented on Python 2.7. It will not work on Python 3.
The machine had a Quadcore CPU and 16 GB RAM, although the BotnetEmulator will, most likely, also work on 8 GB RAM.
Before it can be run, the BotnetEmulator/install-requirements.sh script needs to be executed.
This script will install a collection of tools and Python modules that are required by the Botnet Emulator.
Please note that this might negatively impact the system on which it is executed. It is therefore recommended to install the Botnet Emulator in a virtual Machine
or on a dedicated server.

Execution of an experiment
--------------------------
To execute an experiment just run the appropriate file. It might be necessary to make it executable with chmod +x filename .
It should run for about 5 minutes, except for the OverbotExperiment.py which takes longer.
Afterwards, there will be log file for the experiment under /var/log/botnetemulator.log and one log file per Mininet host under /tmp .
The results of the experiment can be found under /tmp/botnetemulator/ .

Troubleshooting
---------------
Under rare circumstances, Mininet interferes with the network configuration and is unable to reset it after the experiment finishes. In that case the computer should be restarted.
In addition, experiments can fail with bots that cannot ping each other. The /var/log/botnetemulator.log will contain an appropriate error message. 
This is usually because the Floodlight controller was not used. The install-requirements.py sets it up as default,
but if you see this error please make sure Floodlight is used and not the Mininet default controller.

Author
------
Martin Haug, 2214231, 07.09.2016
