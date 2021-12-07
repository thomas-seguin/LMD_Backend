def cleanNullValues(d: dict, parent_key: str = None) -> dict:
  d_copy= {}
  for k, v in d.items():
    if isinstance(v, dict):  
      nested = cleanNullValues(v, k)
      if len(nested.keys()) > 0:
        d_copy.update(nested)
        
    elif v is not None:
      if parent_key is None:
        d_copy[k] = v
      else:
        d_copy[f"{parent_key}.{k}"] = v
  
  return d_copy
