
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Sheila Miguez
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
import argparse
from collections import Counter
import random
import time

from prometheus_client import (
    CollectorRegistry,
    Counter as PrometheusCounter,
    Gauge,
    Summary,
    push_to_gateway,
)

"""
This file contains functions related to monitoring with a Prometheus pushgateway.
Short lived batch jobs are monitored via push rather than pull.
see this for details, https://prometheus.io/docs/instrumenting/pushing/
This example has a fake job called update_devices. I've set it up to demonstrate
counts for processed devices, records of job success or failure, and the run
time for the job.
You should have prometheus and a pushgateway running. Here is a simple
prometheus.yml that assumes prometheus and your pushgateway are running
locally::
    global:
      scrape_interval:     15s
      evaluation_interval: 30s
      # scrape_timeout is set to the global default (10s).
    scrape_configs:
    - job_name: pushgateway
      scrape_interval: 5s
      honor_labels: true
      static_configs:
        - targets: ['localhost:9091']
For this example I've defined the metrics and collector in a global scope.
Your job will need to have access to a collector and the pushgateway hostname.
Django stores this type of information in settings. ymmv. You can fake up
singletons in python. etc.
It would make disabling the instrumentation scaffolding easier if you used
something like a singleton, and it would also make testing easier.
This example doesn't do anything like that.
"""
PUSH_GATEWAY = "localhost:9091"
REGISTRY = CollectorRegistry()

SUCCESS = Gauge("update_devices_last_success_unixtime", "Last time of success")
FAILURE = Gauge("update_devices_last_failure_unixtime", "Last time of failure")
COUNT_UPDATED = Gauge("update_devices_device_count", "Number of devices updated", ["device_type"])
RUN_TIME = Gauge("update_devices_runtime_seconds", "time to finish job")

# You need to register all of the metrics with your registry.  I like doing it
# this way, but you can also pass the registry when you create your metrics.
REGISTRY.register(SUCCESS)
REGISTRY.register(FAILURE)
REGISTRY.register(RUN_TIME)
REGISTRY.register(COUNT_UPDATED)


def monitor_failure(f):
    """
    Add a unixtime to the FAILURE guage when a function raises an exception.
    Simple eample with globals.
    Assumptions for this example:
      * REGISTRY is defined.
      * FAILURE is defined.
      * FAILURE is already registered with REGISTRY
      * if PUSHGATEWAY is not defined it defaults to localhost:9091
    Usage::
        @monitor_failure
        def my_foo_example():
            raise Exception("You have failed me for this one time.")
    On the Prometheus UI, you'll want to graph how long it's been since the last failure::
        time() - update_devices_last_failure_unixtime
    """
    def failure_time(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return result
        except:
            FAILURE.set_to_current_time()
            push_to_gateway(PUSH_GATEWAY, job='pushgateway', registry=REGISTRY)
            raise
    return failure_time


def count_updates(f):
    """
    Monitor devices updated by an update_devices job.
    Simple eample with globals.
    Assumptions for this example:
      * REGISTRY is defined.
      * COUNT_UPDATED is defined.
      * COUNT_UPDATED is already registered with REGISTRY and "device_type" is a valid label.
      * if PUSHGATEWAY is not defined it defaults to localhost:9091
      * if you decorate a function that does not adhere to the update_devices
        interface this is going to blow up in your face. Maybe don't do that.
    """
    def device_type_count(*args, **kwargs):
        """
        For the sake of this example, pretend like humans always decorate a
        function that returns {} or::
            {
                "pci": 123,
                "usb": 123,
            }
        """
        result = f(*args, **kwargs)
        for k,v in result.items():
            COUNT_UPDATED.labels(device_type=k).set(v)
        push_to_gateway(PUSH_GATEWAY, job='pushgateway', registry=REGISTRY)
        return result
    return device_type_count


def monitor_success(guage):
    """
    Add a unixtime to the guage when the decorated function competes successfully.
    Args:
        gauge: a prometheus_client Guage object or any object that provides the same interface.
    This example shows a decorator that accepts a guage as a parameter. Assumptions
    for this example:
      * REGISTRY is defined.
      * The guage is already registered with REGISTRY
      * if PUSHGATEWAY is not defined it defaults to localhost:9091
    Usage::
        foo_success = Gauge("foo_last_success_unixtime", "Last time foo job ran successfully.")
        @set_completion_time(foo_success)
        def my_foo_example():
            pass
    """
    def success_time(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            guage.set_to_current_time()
            push_to_gateway(PUSH_GATEWAY, job='pushgateway', registry=REGISTRY)
            return result
        return wrapper
    return success_time


class DemoException(Exception):
    pass


@RUN_TIME.time()
@monitor_success(SUCCESS)
@monitor_failure
@count_updates
def update_devices(failure_thresehold=95):
    """
    * randomly count pci or usb devices
    * fail at a given thresehold, defaults to 95/100
    * run for a random amount of seconds between 0 and 5
    """
    c = Counter()
    c["pci"] = random.randint(1, 100)
    c["usb"] = random.randint(1, 100)

    sleeptime = random.uniform(0, 5)
    time.sleep(sleeptime)

    fail = random.randint(1, 100)
    if fail > failure_thresehold:
        print("demoing an exception. slept {!r}".format(sleeptime))
        raise DemoException("Demo failure")
    print("demoing a sucess. count {!r}. slept {!r}".format(c, sleeptime))
    return c


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
Demonstrate an instrumented job that pushes to a
pushgateway running on localhost:9091
Press ctl-c to stop.
After running this a few times you should see metrics
like these at <http://localhost:9091/metrics>:
# HELP update_devices_device_count Number of devices updated
# TYPE update_devices_device_count gauge
update_devices_device_count{device_type="pci",instance="",job="pushgateway"} 82
update_devices_device_count{device_type="usb",instance="",job="pushgateway"} 79
# HELP update_devices_last_failure_unixtime Last time of failure
# TYPE update_devices_last_failure_unixtime gauge
update_devices_last_failure_unixtime{instance="",job="pushgateway"} 1.503684346071943e+09
# HELP update_devices_last_success_unixtime Last time of success
# TYPE update_devices_last_success_unixtime gauge
update_devices_last_success_unixtime{instance="",job="pushgateway"} 1.503684366877094e+09
# HELP update_devices_runtime_seconds time to finish job
# TYPE update_devices_runtime_seconds gauge
update_devices_runtime_seconds{instance="",job="pushgateway"} 3.082188844680786
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("thresehold", type=int, default=95, nargs='?', help="thresehold for failure, defaults to > 95%%")
    args = parser.parse_args()

    while True:
        try:
            results = update_devices(args.thresehold)
        except DemoException:
            pass
