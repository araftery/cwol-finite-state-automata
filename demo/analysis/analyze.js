
var margin = {top: 20, right: 80, bottom: 30, left: 50},
    width = 1500 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var x_reverse = d3.scale.linear()
                .domain([0, width])

var y = d3.scale.linear()
    .range([height, 0]);


var left_padding = 30;
var top_padding = 20;


var color = d3.scale.category10();
var differentiated_color = function(name)
{
  if (name == 'CWOL' || name == 'All C')
  {
    return 'darkgreen';
  }
  else if (name == 'Other C')
  {
    return 'lightgreen';
  }
  else if (name == 'CWL')
  {
    return 'steelblue';
  }
  else if (name == 'Only L')
  {
    return 'purple';
  }
  else if (name == 'DWL')
  {
    return 'pink';
  }
  else if (name == 'Other D')
  {
    return 'darkred';
  }
  else if (name == 'DWOL' || name == 'All E')
  {
    return 'red';
  }
  else if (name == 'Unclassified')
  {
    return 'gray';
  }
}


var differentiated_color_change = function(name)
{

  var classes = name.split(" ");
  var name = classes[classes.length - 1];

  if (name == 'cwol' || name == 'allc')
  {
    return 'darkgreen';
  }
  else if (name == 'otherc')
  {
    return 'lightgreen';
  }
  else if (name == 'cwl')
  {
    return 'steelblue';
  }
  else if (name == 'onlyl')
  {
    return 'purple';
  }
  else if (name == 'dwl')
  {
    return 'pink';
  }
  else if (name == 'otherd')
  {
    return 'darkred';
  }
  else if (name == 'dwol' || name == 'alle')
  {
    return 'red';
  }
  else if (name == 'unclassified')
  {
    return 'gray';
  }
}

var combined_color = function(name)
{

  var classes = name.split(" ");
  var name = classes[classes.length - 1];

  if (name == 'cwol' || name == 'allc')
  {
    return 'darkgreen';
  }
  else if (name == 'otherc')
  {
    return 'lightgreen';
  }
  else if (name == 'cwl')
  {
    return 'steelblue';
  }
  else if (name == 'onlyl')
  {
    return 'purple';
  }
  else if (name == 'dwl' || name == 'otherd' || name == 'dwol' || name == 'alle')
  {
    return 'red';
  }
  else if (name == 'unclassified')
  {
    return 'gray';
  }
}

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) { return x(d.gen); })
    .y(function(d) { return y(d.count); });

var stack = d3.layout.stack()
    .values(function(d) { return d.values; });

var area = d3.svg.area()
    .x(function(d) { return x(d.gen); })
    .y0(function(d) { return y(d.y0); })
    .y1(function(d) { return y(d.y0 + d.y); });


var svg1 = d3.select("svg.svg1");

  svg1
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var svg2 = d3.select("svg.svg2");
  
  svg2
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


function create_graph(svg, strat_url, stat_url, key, player)
{
d3.json('setup_vars.json', function(setup_vars){
  for (i in setup_vars)
  {
    d3.select('td.setup_' + i)
      .html(setup_vars[i]);
  }

  d3.json(strat_url, function(error, data) {
    var pop = 0;
    for (i in data)
    {
      pop += data[i][0];
    }


    color.domain(d3.keys(data));


    var strats = stack(color.domain().map(function(name) {
      var values = [];

      for (i in data[name])
      {
          values.push({
              gen: +i,
              y: data[name][i] / pop,
          });
      }

      return {
        name: name,
        values: values,
      }
    }));

    x.domain(d3.extent(strats[0].values, function(d) { return d.gen }));
    x_reverse.range(d3.extent(strats[0].values, function(d) { return d.gen }))

    y.domain([0, 1]);

  var stat_line = d3.svg.line()
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); });

  var stats = {
        total: [],
        at_all: [],
      };

  d3.json(stat_url, function(error, data) {
    for (type in data)
    {
      for (i in data[type])
      {
        if (type == 'at_all')
        {
          data['at_all'][i] = +data['at_all'][i] / (pop * pop);
        }

        stats[type].push({
          x: +i,
          y: +data[type][i],
        });
      }
      stats[type].sort(function(a,b){ return d3.ascending(a.x, b.x); });
    }

    var city = svg.selectAll(".city" + key)
        .data(strats)
      .enter().append("g")
        .attr("class", function(d) { return 'city' + key + ' ' + d.name.toLowerCase().replace(/\s+/g, ''); });

    city.append("path")
        .attr("class", "area area" + key)
        .attr("d", function(d) { return area(d.values); })
        .attr("transform", "translate(" + (left_padding) + ", " + top_padding + ")")
        .style("fill", function(d) { return differentiated_color(d.name); })
        .attr('data-legend', function(d) { if (d.name == 'All L') { return 'Only L'; } else { return d.name } })
        .attr('data-legend-color', function(d) { return differentiated_color(d.name); });

      var focus = svg.append("g")
        .attr("class", "focus")

    stat_line_instance = svg.append("path");

    stat_line_instance
        .datum(stats['total'])
        .attr("class", "stat_line stat_line" + key)
        .attr("d", stat_line)
        .attr("transform", "translate(" + (left_padding) + ", " + top_padding + ")")

    focus.append("svg:line")
          .attr("x1", left_padding)
          .attr("x2", left_padding)
          .attr("y1", top_padding)
          .attr("y2", height + top_padding)
          .attr("class", "hoverline " + key);


    svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .on("mousemove", mousemove)
        .on("click", open_analysis);


    var generation = svg.append("text")
        .attr("y", height - 20 + top_padding)
        .attr("x", left_padding + 20)
        .attr("class", "gen_num gen_num" + key)
        .attr("fill", "white")
        .attr("font-family", "Verdana")
        .attr("font-size", 16)
        .text("Generation: 0")


    d3.select('#line' + key + '_total')
      .on('click', function(){
        d3.select('.stat_line' + key)
          .style('visibility', 'visible')
          .datum(stats['total'])
          .transition()
          .attr("d", stat_line);
      });


    d3.select('#line' + key + '_at_all')
      .on('click', function(){
        d3.select('.stat_line' + key)
          .style('visibility', 'visible')
          .datum(stats['at_all'])
          .transition()
          .attr("d", stat_line);
      });

    d3.select('#line' + key + '_hide')
      .on('click', function(){
        d3.select('.stat_line' + key)
          .style('visibility', 'hidden');
      });

    d3.select('#area_chart' + key + '_show')
      .on('click', function(){
        d3.selectAll('.city' + key)
          .style('visibility', 'visible');

        d3.select('.gen_num' + key)
          .style('fill', 'white');
      });

    d3.select('#area_chart' + key + '_hide')
      .on('click', function(){
        d3.selectAll('.city' + key)
          .style('visibility', 'hidden');

        d3.select('.gen_num' + key)
          .style('fill', 'black');
      });

    d3.select('#defection' + key + '_differentiate')
      .on('click', function(){
        d3.selectAll('.city' + key + '.dwl ' + '.city' + key + '.dwol ' + '.city' + key + '.otherd ' + '.city' + key + '.alle')
          .transition()
          .style('fill', 'red');
      });

    d3.select('#defection' + key + '_combine')
      .on('click', function(){
        d3.selectAll('.city' + key + '.dwl path, ' + '.city' + key + '.dwol path, ' + '.city' + key + '.otherd path, ' + '.city' + key + '.alle path')
          .attr('data-legend-color', 'red')
          .transition()
          .style('fill', 'red');

        svg.select('.legend' + key)
            .call(d3.legend);
      });

    d3.select('#defection' + key + '_differentiate')
      .on('click', function(){
        d3.selectAll('.city' + key + ' path')
          .attr('data-legend-color', function(){
            return differentiated_color_change(d3.select(this.parentNode).attr('class'));
          })
          .transition()
          .style('fill', function(){
            return differentiated_color_change(d3.select(this.parentNode).attr('class'));
          });

          svg.select('.legend' + key)
            .call(d3.legend);

      });


    svg.append("g")
        .attr("class", "x axis xaxis" + key)
        .attr("transform", "translate(" + (left_padding) + "," + (height + top_padding) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis yaxis" + key)
        .attr("transform", "translate(" + left_padding + ", " + top_padding + ")")
        .call(yAxis);






      function mousemove() {
        var x_pos = d3.mouse(this)[0];
        var gen = Math.ceil(x_reverse(x_pos) / setup_vars['milestone']) * setup_vars['milestone'];
        d3.selectAll('.gen_num').text("Generation: " + gen);
        var x_pos = x(gen);
        d3.selectAll('.hoverline')
          .attr("x1", x_pos)
          .attr("x2", x_pos)
      }

      function open_analysis()
      {
        var x_pos = d3.mouse(this)[0];
        var gen = Math.ceil(x_reverse(x_pos) / setup_vars['milestone']) * setup_vars['milestone'];
        var url = "viz/" + gen + "/strategies.html";
        window.open(url, 'name');
      }

    legend = svg.append("g")
      .attr("class","legend legend" + key)
      .attr("transform","translate(" + (left_padding + 30) + ", " + (top_padding + 30) + ")")
      .style("font-size","12px")
      .call(d3.legend)


  });
});
});

d3.json('aggregate_stats.json', function(data){
  var player1 = data.player1;
  var player2 = data.player2;

  d3.select('.cooperates_stats')
    .html(Math.round(player1.toFixed(3) * 100) + '% cooperate');

  d3.select('.continues_stats')
    .html(Math.round(player2.toFixed(3) * 100) + '% continue');
});
}
create_graph(svg1, "player1_tally.json", "player1_stats.json", 1, 1);
create_graph(svg2,  "player2_tally.json", "player2_stats.json", 2, 2);