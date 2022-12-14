import logging
from genie.utils import Dq
from pyats import aetest
from unicon.core.errors import ConnectionError
import time

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all testbed devices"""
        try:
            testbed.connect()
        except ConnectionError:
            self.failed(f"Could not connect to all devices in {testbed.name}")
        # Print log message confirming all devices are in a 'connected' state
        logger.info(f"Connected to all devices in {testbed.name}")
            

class BGPTestcase(aetest.Testcase):
    @aetest.test
    def check_bgp_neighbors(self, testbed):
        """Check number of established BGP neighbors on each device"""
        # Parse BGP neighbor command on each device
        r1_bgp_neighs = testbed.devices["cat8k-rt1"].parse("show bgp neighbors")
        r2_bgp_neighs = testbed.devices["cat8k-rt1"].parse("show bgp neighbors")

        # Capture 'established' neighbors from each device / Set class variables for future comparison
        self.r1_pre_estab_neighbors = Dq(r1_bgp_neighs).contains("Established").get_values("neighbor")
        self.r2_pre_estab_neighbors = Dq(r2_bgp_neighs).contains("Established").get_values("neighbor")

        # Confirm 'established' BGP neighbors were found
        if self.r1_pre_estab_neighbors and self.r2_pre_estab_neighbors:
            self.passed(f"Established neighbors were found for each router.")
        else:
            self.failed("One of the routers has 0 established BGP neighbors.")

    @aetest.test
    def shutdown_bgp(self, testbed):
        """Shutdown BGP neighbors by shutting interfaces"""
        testbed.devices["cat8k-rt1"].configure("interface g4\r shut")
        testbed.devices["cat8k-rt2"].configure("interface g4\r shut")

    @aetest.test
    def check_routing(self, testbed):
        """Check routing tables for recevied BGP routes"""
        # Parse routing tables on each device
        rt1_bgp_routes = testbed.devices["cat8k-rt1"].parse("show ip route")
        rt2_bgp_routes = testbed.devices["cat8k-rt2"].parse("show ip route")
        
        # Drill down to IPv4 AF routes
        rt1_ipv4_routes = rt1_bgp_routes["vrf"]["default"]["address_family"]["ipv4"]["routes"]
        rt2_ipv4_routes = rt2_bgp_routes["vrf"]["default"]["address_family"]["ipv4"]["routes"]

        # Look for specific received BGP routes from each router
        rt1_bgp_route = rt1_ipv4_routes.get("10.60.0.0/24")
        rt2_bgp_route = rt2_ipv4_routes.get("10.50.0.0/24")

        # Determine whether routes are found and pass/fail the test based on the result
        if rt1_bgp_route is not None:
            self.failed(f"BGP route for 10.60.0.0/24 is still present in cat8k-rt1's route table")
        elif rt2_bgp_route is not None:
            self.failed(f"BGP route for 10.50.0.0/24 is still present in cat8k-rt2's route table")
        else:
            self.passed("BGP routes are not found in either routing table.")

    @aetest.test
    def unshut_bgp(self, testbed):
        """Reactivate BGP by unshutting WAN interfaces on each device"""
        testbed.devices["cat8k-rt1"].configure("interface g4\r no shut")
        testbed.devices["cat8k-rt2"].configure("interface g4\r no shut")
        # Allow time for BGP to re-establish
        logger.info("Allow time for BGP to re-establish...")
        time.sleep(20)

    @aetest.test
    def check_post_routing(self, testbed):
        """Check routing tables for recevied BGP routes"""
        # Parse routing tables on each device
        rt1_bgp_routes = testbed.devices["cat8k-rt1"].parse("show ip route")
        rt2_bgp_routes = testbed.devices["cat8k-rt2"].parse("show ip route")
        
        # Drill down to IPv4 AF routes
        rt1_ipv4_routes = rt1_bgp_routes["vrf"]["default"]["address_family"]["ipv4"]["routes"]
        rt2_ipv4_routes = rt2_bgp_routes["vrf"]["default"]["address_family"]["ipv4"]["routes"]

        # Look for received BGP routes from each router
        rt1_bgp_route = rt1_ipv4_routes.get("10.60.0.0/24")
        rt2_bgp_route = rt2_ipv4_routes.get("10.50.0.0/24")

        # Determine whether routes are found and pass/fail the test based on the result
        if rt1_bgp_route is None:
            self.failed(f"BGP route for 10.60.0.0/24 was not found in cat8k-rt1's route table")
        elif rt2_bgp_route is None:
            self.failed(f"BGP route for 10.50.0.0/24 was not found in cat8k-rt2's route table")
        else:
            self.passed("BGP routes are found in both routing tables.")

    @aetest.test
    def check_post_bgp_neighbors(self, testbed):
        """Check number of established BGP neighbors on each device"""
        # Parse BGP neighbor command on each device
        r1_bgp_neighs = testbed.devices["cat8k-rt1"].parse("show bgp neighbors")
        r2_bgp_neighs = testbed.devices["cat8k-rt1"].parse("show bgp neighbors")

        # Capture 'established' neighbors from each device
        r1_post_estab_neighbors = Dq(r1_bgp_neighs).contains("Established").get_values("neighbor")
        r2_post_estab_neighbors = Dq(r2_bgp_neighs).contains("Established").get_values("neighbor")

        # Compare the list of 'established' neighbors with the list of 'established' neighbors found pre-testing
        if self.r1_pre_estab_neighbors == r1_post_estab_neighbors and self.r2_pre_estab_neighbors == r2_post_estab_neighbors:
            self.passed(f"The same number of established neighbors were found on each router.")
        else:
            self.failed("One of the routers have a different number of established BGP neighbors after testing.")

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        """Disconnect from all devices"""
        testbed.disconnect()
        logger.info(f"Disconnected from all devices in {testbed.name}")


# Standalone execution
if __name__ == '__main__':
    from pyats.topology import loader
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Load the testbed file
    cml_tb = loader.load("cml_testbed.yaml")

    # and pass all arguments to aetest.main() as kwargs
    aetest.main(testbed=cml_tb)

    # To run standalone execution:
    # python bgp_testscript.py