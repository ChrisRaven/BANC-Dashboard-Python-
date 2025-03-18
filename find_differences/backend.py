__all__ = ['find_differences']

import threading


def find_differences(A, B, large_neurons, subtract_large_neurons, callback):
  threading.Thread(target=lambda: find_differences_request(A, B, large_neurons, subtract_large_neurons, callback), daemon=True).start()

def find_differences_request(A, B, large_neurons, subtract_large_neurons, callback):
  a_set = set(A)
  b_set = set(B)
  large_neurons_set = set(large_neurons)

  if subtract_large_neurons:
    b_set = b_set | large_neurons_set
  
  a_only = list(a_set - b_set)
  a_plus_b = list(a_set & b_set)
  b_only = list(b_set - a_set)

  callback({
    'a_only': a_only,
    'a_plus_b': a_plus_b,
    'b_only': b_only
  })
