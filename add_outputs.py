# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "onnx",
# ]
# ///
import onnx

def add_intermediate_outputs(input_path: str, output_path: str):
    # Load the model
    model = onnx.load(input_path)
    
    # Add intermediate nodes as outputs
    intermediate_nodes = {
        "Plus30": [1, 8, 28, 28],    # Explicit shape for Plus30
        "Plus112": [1, 16, 14, 14]   # Explicit shape for Plus112
    }

    # Add identity nodes to fork intermediate outputs
    for node_name, shape in intermediate_nodes.items():
        # Find the node with the given name
        for node in model.graph.node:
            if node.name == node_name:
                # Create an Identity node to fork the output
                identity_node = onnx.helper.make_node(
                    'Identity',
                    inputs=[node.output[0]],  # Use the original output
                    outputs=[node_name + '_output'],
                    name=node_name + '_identity'
                )
                
                # Create new output with proper type information and shape
                new_output = onnx.helper.make_tensor_value_info(
                    name=node_name + '_output',
                    elem_type=1,  # FLOAT
                    shape=shape   # Explicit shape
                )
                
                # Add the identity node and new output
                model.graph.node.append(identity_node)
                model.graph.output.extend([new_output])
                break
        
    # Save the modified model
    onnx.save(model, output_path)

if __name__ == "__main__":
    add_intermediate_outputs("public/mnist.onnx", "public/mnist-with-outputs.onnx")
