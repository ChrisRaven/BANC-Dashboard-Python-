__all__ = ['find_differences']

import threading

def find_differences(A, B, callback):
    threading.Thread(target=lambda: find_differences_request(A, B, callback), daemon=True).start()

def find_differences_request(A, B, callback):
    a_set = set(A)
    b_set = set(B)
    
    a_only = list(a_set - b_set)
    a_plus_b = list(a_set & b_set)
    b_only = list(b_set - a_set)

    callback({
      'a_only': a_only,
      'a_plus_b': a_plus_b,
      'b_only': b_only
    })
