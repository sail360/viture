from pathlib import Path
import random
import h5py
import numpy as np

from hloc import extract_features, pairs_from_retrieval

# from projectaria_tools.core import data_provider
# from projectaria_tools.core.stream_id import StreamId
import numpy as np
import imageio.v2 as imageio

ROOT = Path("db_images")
GLOBAL_H5 = Path("/workspace/avis_ucsc_website/static/global-feats.h5")
QUERY_H5 = Path("query-global.h5")
PAIRS_TXT = Path("pairs-query-db.txt")

def extract_query_feature(query_path):
    query_path = Path(query_path)
    conf = extract_features.confs["netvlad"]
    extract_features.main(
        conf,
        query_path.parent,
        image_list=[query_path.name],
        feature_path=QUERY_H5,
        overwrite=True,
    )
    return query_path.name

def retrieve_top_matches(query_name: str, num_matched: int = 10):
    pairs_from_retrieval.main(
        descriptors=QUERY_H5,
        output=PAIRS_TXT,
        num_matched=num_matched,
        query_list=[query_name],
        db_descriptors=GLOBAL_H5,
    )


def print_results():
    print("\nTop retrieved pairs:")
    for line in PAIRS_TXT.read_text().splitlines():
        q, d = line.strip().split()
        print(f"{q}  ->  {d}")


# if __name__ == "__main__":
#     query_path = choose_random_query()
#     query_path = choose_local_query()
#     path = "/workspace/data-store/data/user_folders/JpdonS2FJPSs/public/baskin_map/F25_3.vrs"
#     query_path = choose_random_vrs_query(path)           # vrs frame case

#     print(f"Chosen query path: {query_path}")

#     query_name = extract_query_feature(query_path)
#     retrieve_top_matches(query_name, num_matched=10)
#     print_results()


# aria_mps multi -i /workspace/data-store/data/user_folders/JpdonS2FJPSs/public/baskin_map -o /workspace/data-store/data/user_folders/JpdonS2FJPSs/public/baskin_map/multi_slam_output
# kubectl cp ~/Documents/records.zip avis-deployment:/workspace/data-store/records.zip