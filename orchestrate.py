# orchestrate.py
import yaml
import networkx as nx
import modules

# Load pipeline.yml from pipelines folder
with open('pipeline.yml') as f:
    pipeline = yaml.safe_load(f)

# Create the DAG
G = nx.DiGraph()

# Create an empty string to store our ASCII pipeline representation
ascii_pipeline = ""

# Data dictionary to store the outputs of each module
data_dict = {}

for operation in pipeline['pipeline']:
  module_name = operation['module']
  output_name = operation['output_name']
  inputs = operation['inputs']
  supplement = operation.get('supplement', '')

  # Add node for this operation's output if it doesn't already exist
  G.add_node(output_name)

  # Add edges for inputs
  for i in inputs:
    G.add_edge(i, output_name)

  # Add this operation to our ASCII pipeline representation
  ascii_pipeline += "{} --> {} --> {}\n".format(inputs, module_name, output_name)


print("\033[95mLoading pipeline...\033[00m")
print(ascii_pipeline)

# Now you can use topological sort to get the execution order:
execution_order = list(nx.topological_sort(G))

# And execute the tasks in this order, passing the necessary data between them:
for output_name in execution_order:
  if output_name in data_dict: 
    # skip over inputs that are already defined
    continue

  operation = [item for item in pipeline['pipeline'] if item['output_name'] == output_name][0]
  module_name = operation['module']
  supplement = operation.get('supplement', '')
  
  # Print the module name in red
  print(f"\033[91m{module_name.upper()}\033[00m")

  if hasattr(modules, module_name):
    module_func = getattr(modules, module_name)
    prompt = '\n'.join([data_dict.get(input, '') for input in operation['inputs']])
    prompt += '\n Additional User Input' + supplement
    result, messages = module_func(prompt)
    data_dict[output_name] = result
  else:
    print(f"Warning: No module function '{module_name}'. Ignoring.")

