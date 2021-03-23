# -*- coding: utf-8 -*-
"""This serves as an example of the pipestore hashing.

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import random
import unittest

from ergo_analytics.data_raw import LoadDataFromLocalDisk
from ergo_analytics.aws_utilities import Pipestore
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics.filters import ZeroShiftFilter


class TestPipestore(unittest.TestCase):
    def test_pipestore(self):
        """Simple test of the pipestore."""

        ROOT_DIR = os.path.abspath(os.path.expanduser("."))

        data_format_code = "1"  # in which format is the data coming to us?

        basepath_raw_data = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "data_small.csv"
        )

        assert os.path.isfile(basepath_raw_data)

        put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

        raw_data_loader = LoadDataFromLocalDisk()
        raw_data = raw_data_loader.get_data(
            path=basepath_raw_data,
            destination=put_structured_data_here,
            data_format_code=data_format_code,
        )

        # now pass the raw data through our data filter pipeline:
        pipeline = DataFilterPipeline()
        # instantiate the filters:
        # add something random to ensure the name is diff (triggering new hash):

        # create some new data by randomly modifying the existing data:

        raw_data.iloc[4, 1] += random.randint(1, 1000)
        raw_data.iloc[4, random.randint(2, 4)] += random.randint(1, 1000)

        # names should not change the underlying results, so this will be found in the store:
        pipeline.add_filter(name="fix_osc", filter=FixDateOscillations())
        pipeline.add_filter(name="centering1", filter=DataCentering())
        pipeline.add_filter(name="delta_values", filter=ConstructDeltaValues())
        pipeline.add_filter(name="centering2", filter=DataCentering())
        pipeline.add_filter(name="zero_shift", filter=ZeroShiftFilter())
        pipeline.add_filter(name="window", filter=WindowOfRelevantDataFilter())
        pipeline.add_filter(name="impute", filter=DataImputationFilter())
        pipeline.add_filter(name="quadrant_fix", filter=QuadrantFilter())

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        first_hash = pipeline._most_recent_pipestore_hash
        assert first_hash is not None
        assert not pipeline._found_in_pipestore

        # just test data, so delete:
        pst = Pipestore()
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert this_exists
        pst.delete_data(hash=first_hash)
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert not this_exists

        # run it again - first_hash should not initially be found
        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        first_hash = pipeline._most_recent_pipestore_hash
        assert first_hash is not None
        assert not pipeline._found_in_pipestore

        # just test data, so delete:
        pst = Pipestore()
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert this_exists
        pst.delete_data(hash=first_hash)
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert not this_exists

    def test_delete(self):
        """Test delete from pipestore."""

        ROOT_DIR = os.path.abspath(os.path.expanduser("."))

        data_format_code = "1"  # in which format is the data coming to us?

        basepath_raw_data = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "data_small.csv"
        )

        assert os.path.isfile(basepath_raw_data)

        put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

        raw_data_loader = LoadDataFromLocalDisk()
        raw_data = raw_data_loader.get_data(
            path=basepath_raw_data,
            destination=put_structured_data_here,
            data_format_code=data_format_code,
        )

        # now pass the raw data through our data filter pipeline:
        pipeline = DataFilterPipeline()
        # instantiate the filters:
        # add something random to ensure the name is diff (triggering new hash):

        # create some new data by randomly modifying the existing data:

        raw_data.iloc[4, 1] += random.randint(1, 1000)
        raw_data.iloc[4, random.randint(2, 4)] += random.randint(1, 1000)

        # names should not change the underlying results, so this will be found in the store:
        pipeline.add_filter(name="name11", filter=FixDateOscillations())
        pipeline.add_filter(name="name12", filter=DataCentering())

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        this_hash = pipeline._most_recent_pipestore_hash
        assert this_hash is not None
        assert not pipeline._found_in_pipestore

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        this_hash = pipeline._most_recent_pipestore_hash
        assert this_hash is not None
        assert pipeline._found_in_pipestore

        pst = Pipestore()
        this_exists, _ = pst.pipestore_hash_exists(hash=this_hash)
        assert this_exists
        pst.delete_data(hash=this_hash)
        this_exists, _ = pst.pipestore_hash_exists(hash=this_hash)
        assert not this_exists

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        this_hash = pipeline._most_recent_pipestore_hash
        assert this_hash is not None
        assert not pipeline._found_in_pipestore

        pst.delete_data(hash=this_hash)
        this_exists, _ = pst.pipestore_hash_exists(hash=this_hash)
        assert not this_exists

    def test_names_should_not_matter(self):
        """Filter names should not matter."""

        ROOT_DIR = os.path.abspath(os.path.expanduser("."))

        data_format_code = "1"  # in which format is the data coming to us?

        basepath_raw_data = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "data_small.csv"
        )

        assert os.path.isfile(basepath_raw_data)

        put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

        raw_data_loader = LoadDataFromLocalDisk()
        raw_data = raw_data_loader.get_data(
            path=basepath_raw_data,
            destination=put_structured_data_here,
            data_format_code=data_format_code,
        )

        # now pass the raw data through our data filter pipeline:
        pipeline = DataFilterPipeline()
        # instantiate the filters:
        # add something random to ensure the name is diff (triggering new hash):

        # create some new data by randomly modifying the existing data:

        raw_data.iloc[4, 1] += random.randint(1, 1000)
        raw_data.iloc[4, random.randint(2, 4)] += random.randint(1, 1000)

        # names should not change the underlying results, so this will be found in the store:
        pipeline.add_filter(name="name11", filter=FixDateOscillations())
        pipeline.add_filter(name="name12", filter=DataCentering())

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        first_hash = pipeline._most_recent_pipestore_hash
        assert first_hash is not None
        assert not pipeline._found_in_pipestore

        # now run again:
        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )
        second_hash = pipeline._most_recent_pipestore_hash
        assert second_hash is not None
        assert pipeline._found_in_pipestore

        assert first_hash == second_hash

        # names should not change the underlying results, so this will be found in the store:
        pipeline = DataFilterPipeline()
        pipeline.add_filter(name="name21", filter=FixDateOscillations())
        pipeline.add_filter(name="name22", filter=DataCentering())

        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )

        third_hash = pipeline._most_recent_pipestore_hash
        assert third_hash is not None
        assert pipeline._found_in_pipestore

        # now run again:
        _ = pipeline.run(
            on_raw_data=raw_data,
            with_format_code=data_format_code,
            num_rows_per_chunk=100,
        )
        fourth_hash = pipeline._most_recent_pipestore_hash
        assert fourth_hash is not None
        assert pipeline._found_in_pipestore

        assert first_hash == second_hash == third_hash == fourth_hash

        # just test data, so delete:
        pst = Pipestore()
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert this_exists
        pst.delete_data(hash=first_hash)
        this_exists, _ = pst.pipestore_hash_exists(hash=first_hash)
        assert not this_exists
