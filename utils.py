# New imports for visualization
import networkx as nx
from pyvis.network import Network
from typing import List
from langchain_community.graphs.graph_document import GraphDocument

# 🎨 Function to visualize the graph documents 
def visualize_graph_documents(graph_documents: List[GraphDocument], output_filename="knowledge_graph.html"):
    """
    Manually converts LangChain GraphDocument to NetworkX and visualizes with Pyvis.
    """
    # 1. Initialize NetworkX Graph (MultiDiGraph allows directed edges and multiple edges between nodes)
    G = nx.MultiDiGraph()

    # 2. Add Nodes
    # LLMGraphTransformer returns a list of GraphDocuments. We iterate through the first one.
    if not graph_documents:
        print("No graph documents to visualize.")
        return

    # Assuming a single document conversion, but the logic works for multiple
    doc = graph_documents[0] 
    
    # Store nodes to ensure unique keys for NetworkX/Pyvis
    node_map = {} 

    for node in doc.nodes:
        # Create a unique ID for NetworkX node (Node(id='Name', type='Type'))
        node_id = f"{node.type}:{node.id}"
        node_map[str(node.model_dump())] = node_id

        # Prepare tooltip (title) HTML string with properties
        title_html = f"<b>{node.type}: {node.id}</b><hr style='margin: 4px 0;'>"
        for prop, value in node.properties.items():
            # Add specified properties to the tooltip for rich detail
            title_html += f"<i>{prop.replace('_', ' ').title()}</i>: {value}<br>"
        
        # Add node to NetworkX, carrying attributes
        G.add_node(
            node_id, 
            label=node.id,  # Display name on the node
            group=node.type, # Use type for grouping/coloring
            title=title_html, # Pyvis tooltip content
        )

    # 3. Add Relationships (Edges)
    for relationship in doc.relationships:
        source_id = node_map.get(str(relationship.source.model_dump()))
        target_id = node_map.get(str(relationship.target.model_dump()))

        if source_id and target_id:
            G.add_edge(
                source_id,
                target_id,
                label=relationship.type, # Display relationship type on the edge
                title=relationship.type, # Edge tooltip
                # You can add relationship properties here if your transformer extracts them
            )

    # 4. Visualize with Pyvis
    net = Network(
        notebook=True, 
        cdn_resources='in_line', 
        height='750px', 
        width='100%', 
        bgcolor='#222222', 
        font_color='white'
    )
    
    # Import the NetworkX graph into Pyvis
    net.from_nx(G)

    # Optional: Display configuration buttons to let you tweak physics/layout
    net.show_buttons(filter_=['physics']) 
    
    # Save the interactive visualization to an HTML file
    net.save_graph(output_filename)
    print(f"✨ Interactive graph saved to {output_filename}")
