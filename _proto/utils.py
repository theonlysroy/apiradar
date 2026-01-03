import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel

class APIEndpoint(BaseModel):
  method: str
  url: str

def extract_endpoints(spec: Dict[str, str | Any]) -> List[APIEndpoint]:
  """
  Extract all HTTP endpoints from an OpenAPI specification.

  Parses the 'paths' object from the specification and returns a list of
  APIEndpoint objects for each method defined at each path.

  Example OpenAPI paths structure:
    "paths": {
      "/hello": {
        "get": { ... },
        "post": { ... }
      }
    }

  Args:
      spec: A valid OpenAPI specification dictionary.

  Returns:
      List of APIEndpoint objects with method (lowercase) and URL.
      Example: [APIEndpoint(method='get', url='/users'), 
                APIEndpoint(method='post', url='/user')]

  Raises:
      AttributeError: If the 'paths' object is not defined in the specification.
  """
  paths: Dict[Any] = spec.get('paths', {})
  if not paths:
    raise AttributeError('Paths not defined in the specification')
  
  endpoints: List[APIEndpoint] = []
  for url, methods in paths.items():
    for method in methods.keys():
      endpoints.append(APIEndpoint(method=method.lower(), url=url).model_dump())

  return endpoints

def load_prompts(spec: Dict[str, str | Any], analysis: str = 'summary') -> str:
  """
  Helper method to load the prompts for the specific analysis type and append the api specification
  as json

  Args:
    analysis: str Type of the analysis `summary`, `security` or `edge_cases`
    spec: dict Parsed api endpoint specification
  
  Returns:
    Formatted prompt string  
  
  Raises:
    AttributeError: if analysis undefined or does not match with the predefined cases
  """
  prompt_map = {
    'summary': 'prompts/endpoint_summary.md',
    'security': 'prompts/endpoint_security_analysis.md',
    'edge_cases': 'prompts/endpoint_edge_cases.md'
  }
  if analysis not in prompt_map.keys():
    raise AttributeError(f"{analysis} type is not a valid analysis")
  
  prompt_file = str(Path(prompt_map.get(analysis)).resolve())
  with open(prompt_file, 'r') as f:
    prompt_template = f.read()
  instructions = prompt_template.format(
    ENDPOINT_SPECIFICATION=json.dumps(spec)
  )
  return instructions