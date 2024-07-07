fetch('/data').then(function(response) {
    return response.json();
}).then(function(data) {
    var nodes = new vis.DataSet(data.nodes.map(node => {
        if (node.image) {
            return { ...node, shape: 'image', image: node.image };
        } else {
            return { ...node, shape: 'dot', image: undefined };
        }
    }));
    var edges = new vis.DataSet(data.edges);
    
    var container = document.getElementById('visualization');
    
    var graphData = {
        nodes: nodes,
        edges: edges
    };
    
    var options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#000'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            shadow: true,
            color: {
                color:'#848484',
                highlight:'#848484',
                hover: '#848484',
                inherit: 'from',
                opacity: 0.7
            }
        },
        interaction: {
            hover: true,
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -30000,
                centralGravity: 0.3,
                springLength: 95,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.1
            },
            solver: 'barnesHut',
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 100,
                onlyDynamicEdges: false,
                fit: true
            }
        },
        layout: {
            hierarchical: {
                enabled: false,
                levelSeparation: 150,
                nodeSpacing: 100,
                treeSpacing: 200,
                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true,
                direction: 'UD',
                sortMethod: 'hubsize'
            }
        }
    };
    
    var network = new vis.Network(container, graphData, options);
});
