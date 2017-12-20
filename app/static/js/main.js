$(document).ready(function() {

  $('#slide_1').show();
  $('#slide_2').hide();
  $('#slide_3').hide();
  $('#loader').hide();

  var margin = {top: 20, right: 120, bottom: 20, left: 120},
      width = 960 - margin.right - margin.left,
      height = 800 - margin.top - margin.bottom;

  var i = 0, duration = 750, root;

  var tree = d3.layout.tree().size([height, width]);

  var diagonal = d3.svg.diagonal().projection(function(d) {
    return [d.y, d.x];
  });

  function searchTree(obj, search, path) {
    if (obj.name === search) {
      path.push(obj);
      return path;
    } else if (obj.children || obj._children) {
      var children = (obj.children) ? obj.children : obj._children;
      for (var i = 0; i < children.length; i++) {
        path.push(obj);
        var found = searchTree(children[i], search, path);
        if (found) {
          return found;
        } else {
          path.pop();
        }
      }
    } else {
      return false;
    }
  }

  function extract_select2_data(node, leaves, index) {
    if (node.children) {
      for (var i = 0; i < node.children.length; i++) {
        index = extract_select2_data(node.children[i], leaves, index)[0];
      }
    } else {
      leaves.push({id: ++index, text: node.name});
    }
    return [index, leaves];
  }

  function openPaths(paths) {
    console.log(paths);
    for (var i = 0; i < paths.length; i++) {
      if (paths[i].name !== '1') {
        paths[i].class = 'found';
        if (paths[i]._children) {
          paths[i].children = paths[i]._children;
          paths[i]._children = null;
        }
        update(paths[i]);
      }
    }
  }

  var svg =
      d3.select('#collapsable')
          .append('svg')
          .attr('width', width + margin.right + margin.left)
          .attr('height', height + margin.top + margin.bottom)
          .append('g')
          .attr(
              'transform', 'translate(' + margin.left + ',' + margin.top + ')');
  d3.csv('path/to/data.csv', function(error, data) {
    data = data.filter(function(node) {
      if (node['icd_code'] === '') {
        return false;
      } else {
        return true;
      }
    })
    var dataMap = data.reduce(function(map, node) {
      var code = node.icd_code.substr(0, 1);

      if (code in map) {
        map[code].push(node);
      } else {
        map[code] = [];
        map[code].push(node);
      }
      return map;
    }, {});

    for (var key in dataMap) {
      dataMap[key] = dataMap[key].reduce(function(map, node) {
        var code = node.icd_code.substr(0, 2);

        if (code in map) {
          map[code].push(node);
        } else {
          map[code] = [];
          map[code].push(node);
        }
        return map;
      }, {})
    }

    for (var key in dataMap) {
      for (var val in dataMap[key]) {
        dataMap[key][val] = dataMap[key][val].reduce(function(map, node) {
          var code = node.icd_code.substr(0, 3);

          if (code in map) {
            map[code].push(node);
          } else {
            map[code] = [];
            map[code].push(node);
          }
          return map;
        }, {})
      }
    }

    var treeData = {
      'name': 'root',
      'children': []
    };

    Object.keys(dataMap).forEach(function(key, i) {
      treeData['children'].push({'name': key, 'children': []});
      Object.keys(dataMap[key]).forEach(function(val, j) {
        treeData['children'][i]['children'].push({
          'name': val,
          'children': []
        });
        Object.keys(dataMap[key][val]).forEach(function(kal, k) {
          var dx = dataMap[key][val][kal].map(function(v) {
            v['name'] = v['hamd_id'];
            return v;
          });

            treeData['children'][i]['children'][j]['children'].push(
                {'name': kal, 'children': dx});
        });
      });
    });

    root = treeData;
    root.x0 = height / 2;
    root.y0 = 0;

    update(root);

    function collapseAll() {
      root.children.forEach(collapse);
      collapse(root);
      update(root);
    }

    collapseAll();
  });

  function expand(d) {
    var children = (d.children) ? d.children : d._children;
    if (d._children) {
      d.children = d._children;
      d._children = null;
    }
    if (children) children.forEach(expand);
  }

  function expandAll() {
    expand(root);
    update(root);
  }

  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }

  d3.select(self.frameElement).style('height', '800px');

  function update(source) {
    var nodes = tree.nodes(root).reverse(), links = tree.links(nodes);

    nodes.forEach(function(d) {
      d.y = d.depth * 180;
    });

    var node = svg.selectAll('g.node').data(nodes, function(d) {
      return d.id || (d.id = ++i);
    });

    var nodeEnter =
        node.enter()
            .append('g')
            .attr('class', 'node')
            .attr(
                'transform',
                function(d) {
                  return 'translate(' + source.y0 + ',' + source.x0 + ')';
                })
            .on('click', click);

    var minRadius = 5;
    var maxRadius = 8;
    var scale = d3.scale.linear().range([minRadius, maxRadius]);

    nodeEnter.append('circle').attr('r', 4.5).style('fill', function(d) {
      return d._children ? 'lightsteelblue' : '#fff';
    });

    nodeEnter.append('text')
        .attr(
            'x',
            function(d) {
              return d.children || d._children ? -10 : 10;
            })
        .attr('dy', '.35em')
        .attr(
            'text-anchor',
            function(d) {
              return d.children || d._children ? 'end' : 'start';
            })
        .text(function(d) {
          return d.name;
        })
        .style('fill-opacity', 1e-6);

    var nodeUpdate =
        node.transition().duration(duration).attr('transform', function(d) {
          return 'translate(' + d.y + ',' + d.x + ')';
        });

    nodeUpdate.select('circle')
        .attr(
            'r',
            4.5)
        .style(
            'fill',
            function(d) {
              if (d.class === 'found') {
                return '#ff4136';  // red
              } else if (d._children) {
                return 'lightsteelblue';
              } else {
                return '#fff';
              }
            })
        .style('stroke', function(d) {
          if (d.class === 'found') {
            return '#ff4136';  // red
          }
        });

    nodeUpdate.select('text').style('fill-opacity', 1);

    var nodeExit =
        node.exit()
            .transition()
            .duration(duration)
            .attr(
                'transform',
                function(d) {
                  return 'translate(' + source.y + ',' + source.x + ')';
                })
            .remove();

    nodeExit.select('circle').attr('r', 1e-6);

    nodeExit.select('text').style('fill-opacity', 1e-6);

    var link = svg.selectAll('path.link').data(links, function(d) {
      return d.target.id;
    });

    link.enter()
        .insert('path', 'g')
        .attr('class', 'link')
        .attr('d', function(d) {
          var o = {x: source.x0, y: source.y0};
          return diagonal({source: o, target: o});
        });

    link.transition()
        .duration(duration)
        .attr('d', diagonal)
        .style('stroke', function(d) {
          if (d.target.class === 'found') {
            return '#ff4136';
          }
        });

    link.exit()
        .transition()
        .duration(duration)
        .attr(
            'd',
            function(d) {
              var o = {x: source.x, y: source.y};
              return diagonal({source: o, target: o});
            })
        .remove();

    nodes.forEach(function(d) {
      d.x0 = d.x;
      d.y0 = d.y;
    });
  }

  function click(d) {
    if (d.children) {
      d._children = d.children;
      d.children = null;
    } else {
      d.children = d._children;
      d._children = null;
    }
    update(d);
  }

  $('#btn_visualize').click(function() {
    $('#slide_1').hide();
    $('#loader').hide();
    $('#slide_2').hide();
    $('#slide_3').show();
  });

  $('#btn_summary').click(function() {
    var text = $('#summary').val();

    $('#slide_1').fadeOut(400, function() {
      $('#loader').fadeIn(400, function() {
      });
    });

    $.ajax({
      url: 'http://127.0.0.1:5000/get_info?q=' + text,
      error: function(err) {
        $('#slide_1').hide();
        $('#loader').hide();
        $('#slide_2').show();
        $('#slide_3').hide();
        console.log(err);
      },
      success: function(data) {
        var flag = true;
        if (data['text'] == '') {
          $('#slide_1').show();
          $('#loader').hide();
          $('#slide_2').hide();
          $('#slide_3').hide();
        } else {
          $('#slide_1').hide();
          $('#loader').hide();
          $('#slide_2').show();
          $('#slide_3').hide();
          $('#marked_text').html(data['text']);
          html = '<ul>';
          for (var item of data['icd']) {
            html += '<li>';
            html += item.toString();
            html += '</li>';

            var paths = searchTree(root, item.toString(), []);
            console.log(paths);
            if (typeof (paths) !== 'undefined') {
              openPaths(paths);
              flag = false;
            } else {
              console.log('not found!');
            }
          }
          html += '</ul>';
          if (flag) {
            var paths = searchTree(root, 'Q89', []);
            if (typeof (paths) !== 'undefined') {
              openPaths(paths);
            } else {
              console.log('not found!');
            }
          }
          $('#icd_codes').html(html);
        }
      },
      type: 'GET'
    });
  });
});
