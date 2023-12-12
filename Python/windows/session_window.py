#  Copyright 2022 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# standard libraries
import json
import logging

# third party libraries
from apache_beam import (  # noqa:E501
    CombinePerKey,
    DoFn,
    ParDo,
    Pipeline,
    WindowInto,
    window,
)
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.options.pipeline_options import PipelineOptions

INPUT_TOPIC = "projects/pubsub-public-data/topics/taxirides-realtime"


class ParseMessages(DoFn):
    """
    The input messages are based on key-value pairs
    ('ride_status': 'passenger_count').
    Parse data 'ride_status' and 'passenger_count' from messages
    """

    def process(self, element):
        parsed = json.loads(element.decode("utf-8"))
        if parsed["ride_status"].lower() != "enroute":
            ride_status = parsed["ride_status"]
            passenger_count = parsed["passenger_count"]
            yield (ride_status, passenger_count)


class WriteOutputs(DoFn):
    """Log the outputs"""

    def process(self, element):
        ride_id = element[0]
        meter_cost = element[1]
        logging.info("Ride id %s costed %f", ride_id, meter_cost)


def run(argv=None):
    # Parsing arguments
    class SessionWindowOptions(PipelineOptions):
        @classmethod
        def _add_argparse_args(cls, parser):
            parser.add_argument(
                "--input_topic",
                help='Input PubSub topic of the form "projects/<PROJECT>/topics/<TOPIC>."',  # noqa:E501
                default=INPUT_TOPIC,
            )

    options = SessionWindowOptions(streaming=True)

    # Defining our pipeline and its steps
    with Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> ReadFromPubSub(topic=options.input_topic)
            | "ParseMessages" >> ParDo(ParseMessages())
            # Apply Session Window of time gap of at least 120 seconds
            | "ApplySessionWindow" >> WindowInto(window.Sessions(120))
            | "SumPerKey" >> CombinePerKey(sum)
            | "LogOutputs" >> ParDo(WriteOutputs())
        )


if __name__ == "__main__":
    run()
