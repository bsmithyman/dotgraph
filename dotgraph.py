#!/usr/bin/env python

import time
import networkx
from networkx.readwrite import json_graph
from IPython.core import display
import json

class DotGraph(object):
    '''
    Class that returns various representations of the directed graph
    in a 'dot' file. This includes converting to NetworkX graph object,
    Python dictionary, JSON, and HTML with d3.js rendering (which can
    be displayed inline in an IPython/Jupyter notebook).
    '''
    
    # Base template adapted from force directed graph examples by
    # Mike Bostock at http://bl.ocks.org/mbostock
    _template = '''
    <div id="%(uniqueID)s"></div>
    <style>
    .node {
        stroke-width: 1.5px;
    }
    .node text {
        color: black;
        font: 10px sans-serif;
    }
    .link {
        fill: none;
        stroke: #bbb;
    }
    </style>

    <script>
    var graph = %(JSONData)s;
    
    require.config({paths: {d3: "https://d3js.org/d3.v3.min"}});
    
    require(["d3"], function(d3) {
    
        var width = 1000, height = 450;
        var rwidth = 150, rheight=20;
        var rr = 10;
        var color = d3.scale.category10();
        var domain = [0, 1, 2, 3];
        color.domain(domain);
        
        var force = d3.layout.force()
            .charge(-200)
            .linkDistance(50)
            .linkStrength(2)
            .size([width, height]);
            
        var svg = d3.select("#%(uniqueID)s").select("svg");
        
        if (svg.empty()) {
            svg = d3.select("#%(uniqueID)s").append("svg")
                        .attr("width", width)
                        .attr("height", height);
        }
        
        var nodes = graph.nodes.slice(),
        links = [],
        bilinks = [];
      
        graph.links.forEach(function(link) {
            var s = nodes[link.source],
            t = nodes[link.target],
            i = {}; // intermediate node
            nodes.push(i);
            links.push({source: s, target: i}, {source: i, target: t});
            bilinks.push([s, i, t]);
        });
        
        force.nodes(nodes)
            .links(links)
            .start();
            
        var link = svg.selectAll(".link")
            .data(bilinks)
            .enter().append("path")
            .attr("class", "link");
            
        var node = svg.selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(force.drag);
            
        node.append("rect")
            .attr("x", -rwidth/2)
            .attr("y", -rheight/2)
            .attr("width", rwidth)
            .attr("height", rheight)
            .attr("rx", rr)
            .attr("ry", rr)
            .style("fill", "white")
            .style("stroke", "black");
        
        node.append("text")
            .attr("dx", 0)
            .attr("dy", 3)
            .attr("text-anchor", "middle")
            .text(function(d) { return d.label; });
            
        node.append("title")
            .text(function(d) { return d.label; });
            
        force.on("tick", function() {
            link.attr("d", function(d) {
                return "M" + d[0].x + "," + d[0].y + "S" + d[1].x + "," + d[1].y + " " + d[2].x + "," + d[2].y;
            });
            
            node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        });
    });
    </script>
    '''
    
    def __init__(self, infile, template=None):
        '''
        Initialize DotGraph
        
        Args:
            infile (str):       Input file in dot format
            template (str):     Input file for HTML template

        Returns:
            new DotGraph instance
        '''
        
        if template is not None:
            self._template = template
        
        self.infile = infile
        
    @property
    def graph(self):
        'Returns NetworkX graph representation'
        
        return networkx.read_dot(self.infile)
    
    @property
    def dict(self):
        'Returns dictionary representation'
        
        return json_graph.node_link_data(self.graph)
    
    @property
    def json(self):
        'Returns JSON representation'
        
        if not hasattr(self, '_jenc'):
            self._jenc = json.JSONEncoder()
        return self._jenc.encode(self.dict)
        
    @property
    def html(self):
        'Returns HTML representation'
        
        formatDict = {
            'uniqueID': 'Graph%s'%hash(time.time()),
            'JSONData': self.json,
        }
        
        return self._template%formatDict
    
    def render(self):
        'Returns IPython display representation'
        
        return display.HTML(data=self.html)._repr_html_()


if __name__ == '__main__':
    import sys

    infile = sys.argv[1]
    dg = DotGraph(infile)

    if len(sys.argv) > 2:
        outfile = sys.argv[2]
        with open(outfile, 'w') as fp:
            fp.write(dg.html)
    else:
        sys.stdout.write(dg.html)

else:
    try:
        get_ipython().display_formatter.formatters['text/html'].for_type(DotGraph, DotGraph.render)
    except NameError:
        pass
