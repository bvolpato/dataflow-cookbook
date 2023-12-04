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

import logging

import apache_beam as beam
from apache_beam import Create
from apache_beam import GroupByKey
from apache_beam import Map


def run(argv=None):
  # Define the input key-value pairs
  elements = [
      ("Mammal", "Dog"),
      ("Mammal", "Cat"),
      ("Fish", "Salmon"),
      ("Amphibian", "Snake"),
      ("Bird", "Eagle"),
      ("Bird", "Owl"),
      ("Mammal", "Algo")
  ]

  # Create a PCollection of elements defined above with beam.Create().
  # Use beam.GroupByKey() to group elements by their key.
  with beam.Pipeline() as p:
    output = (
        p | "Create Elements" >> Create(elements)
          | "Group Elements" >> GroupByKey()
          | "Log" >> Map(logging.info))


if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  run()
