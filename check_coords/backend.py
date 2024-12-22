__all__ = ['check_coords']

import threading
import banc
from utils.backend import *


def check_coords(data, callback):
  threading.Thread(target=lambda: check_coords_request(data, callback), daemon=True).start()

def check_coords_request(data, callback):
  segment_ids, coords = [], []
  for coord in data.split(';'):
    seg_id, coord_str = coord.split(':')
    segment_ids.append(int(seg_id))
    coords.append(coord_str.split(','))

  returned_segment_ids = banc.lookup.segid_from_pt(coords)
  returned_segment_ids = set(map(int, returned_segment_ids))

  valid_coords = []
  invalid_segment_ids = []

  coords_len = len(coords)
  for i, segment_id in enumerate(segment_ids):
    if segment_id in returned_segment_ids:
      if i < coords_len:
        valid_coords.append(coords[i])
    else:
      invalid_segment_ids.append(segment_id)

  valid_coords = ';'.join([','.join(map(str, coord)) for coord in valid_coords])
  callback(valid_coords, invalid_segment_ids)
