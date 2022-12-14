from dotenv import load_dotenv
from pyats.topology import loader
from pyats.easypy import run

def main(runtime):
    # Load environment variables
    load_dotenv()
    
    # Load the testbed file
    cml_tb = loader.load("cml_testbed.yaml")
    
    # Set job name
    runtime.job.name = "Dec15-2022-TTTT"

    run(testscript="bgp_testscript.py", runtime=runtime, testbed=cml_tb)

    # To run job:
    # pyats run job bgp_jobfile.py

    # To run job w/ testbed file arg:
    # pyats run job bgp_jobfile.py --testbed-file cml_testbed.yaml