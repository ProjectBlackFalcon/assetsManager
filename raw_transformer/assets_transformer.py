import sys
import os
import time
from multiprocessing import Pool, cpu_count

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'PyDofus_mod')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raw_transformer')))
import argparse
import os

import d2o_unpack
import d2i_unpack
import d2p_unpack

from pipelines import named_recipes
from pipelines import id_2_hdv
from pipelines import id_2_name
from pipelines import id_2_type
from pipelines import effect_id_2_name
from pipelines import rune_2_id
from pipelines import equipments
from pipelines import maps_unpacker
from pipelines import itemid_to_itemiconid
from pipelines import fmable_stats
from pipelines import pathfinder_graph
from pipelines import server_2_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assets Transformer')
    parser.add_argument('dofusdir', type=str, help='Dofus root directory')
    root = parser.parse_args().dofusdir

    # root = 'input'

    for file in os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'definitive_output'))):
        if file.endswith('.json'):
            os.remove(os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'definitive_output/') + file))

    files_paths = {'d2i': [], 'd2o': [], 'd2p': [], 'ele': []}
    files = os.walk(root)
    for root, dirs, files in files:
        for file in files:
            if file.endswith('d2i'):
                files_paths['d2i'].append(root + '/' + file)
            if file.endswith('d2o'):
                files_paths['d2o'].append(root + '/' + file)
            if file.endswith('d2p'):
                files_paths['d2p'].append(root + '/' + file)
            if file.endswith('ele'):
                files_paths['ele'].append(root + '/' + file)

    print('Unpacking source files')
    init_start = time.time()
    with Pool(cpu_count() - 1) as p:
        p.map(d2o_unpack.unpack, [[file_path] for file_path in files_paths['d2o']])  # Items, Recipes, Effects...
        p.map(d2p_unpack.unpack, [[file_path] for file_path in files_paths['d2p']])
        p.map(d2i_unpack.unpack, [[file_path] for file_path in files_paths['d2i']])  # i18n_fr
    print('Done unpacking in ', time.time() - init_start)

    print('Applying transformations')
    start = time.time()
    maps_unpacker.generate_map_info()
    pathfinder_graph.generate()
    itemid_to_itemiconid.generate()
    named_recipes.generate()
    id_2_hdv.generate()
    id_2_name.generate()
    id_2_type.generate()
    effect_id_2_name.generate()
    rune_2_id.generate()
    equipments.generate()
    fmable_stats.generate()
    server_2_id.generate()
    print('Done in', time.time() - start)
    print('Total time: {} minutes, {}s'.format(round(time.time() - init_start) // 60, round(time.time() - init_start) % 60))

    'python raw_transformer\assets_transformer.py raw_transformer\input'
