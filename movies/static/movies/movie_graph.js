document.addEventListener('DOMContentLoaded', function () {
  const autocomplete = document.getElementById("autocomplete");
  const resultsHTML = document.getElementById("results");

  document.getElementById("autocomplete").oninput = function () {
    document.getElementById("description").style.display = "none";
    document.getElementById("warning").innerHTML = "";
    // let results = [];
    const userInput = this.value;
    resultsHTML.innerHTML = "";
    if (userInput.length > 2) {
      // results = getResults(userInput);

      if (myTimeout) {
        clearTimeout(myTimeout);
      }

      myTimeout = setTimeout(function () {

        document.getElementById("warning").innerHTML = "Searching...";

        fetch('/search?q=' + userInput)
          .then(response => response.json())
          .then(movies => {
            search_results = movies;

            let length = search_results.length;

            if (length == 0) {
              document.getElementById("warning").innerHTML = "No results.";
            } else {
              document.getElementById("warning").innerHTML = "";
              resultsHTML.style.display = "block";
              for (i = 0; i < 10; i++) {
                resultsHTML.innerHTML += "<li>" + movies[i].title + "</li>";
              }
            }

          })
      }, 1000);
    }
  };

  document.getElementById("results").onclick = function (event) {
    const setValue = event.target.innerText;
    autocomplete.value = setValue;
    this.innerHTML = "";
    document.getElementById("warning").innerHTML = "";

    movie2 = search_results.filter(obj => {
      return obj.title === setValue
    })[0].id;

    document.getElementById("movie2").value = movie2;

    let error;
    for (i = 0; i < user_graph.length; i++) {
      if (movie2 == user_graph[i].id) {
        error = 'This movie is already connected to this graph.'
      }
    }

    if (error) {
      document.getElementById("warning").innerHTML = error;
    } else {
      document.getElementById("description").style.display = "block";
    }
  }
});

function getResults(input) {
  console.log(other_movies);
  const results = [];
  for (i = 0; i < other_movies.length; i++) {
    if (input.toLowerCase() === other_movies[i].slice(0, input.length).toLowerCase()) {
      results.push(other_movies[i]);
    }
  }
  return results;
}

var scatter_radius = 10;
var search_results = [];
var user_graph;
var movie2;
var movie1;
var myTimeout;

fetch(`/graph/${movie_id}`)
  .then(response => response.json())
  .then(data => {
    user_graph = data.nodes;
    var c10 = d3.scale.category10();
    var svg = d3.select("svg");
    //.attr("width", graph_width)
    //.attr("height", graph_height);

    var links = svg.selectAll("link")
      .data(data.links)
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("x1", function (l) {
        var sourceNode = data.nodes.filter(function (d, i) {
          return i == l.source
        })[0];
        d3.select(this).attr("y1", sourceNode.y);
        return sourceNode.x
      })
      .attr("x2", function (l) {
        var targetNode = data.nodes.filter(function (d, i) {
          return i == l.target
        })[0];
        d3.select(this).attr("y2", targetNode.y);
        return targetNode.x
      })
      .attr("fill", "none")
      .attr("stroke", "red");

    var nodes = svg.selectAll("node")
      .data(data.nodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")" })

    nodes.append("circle")
      .attr("r", "10")

    nodes.append("text")
      .attr("x", 12)
      .attr("dy", ".35em")
      .text(function (d) { return d.name });
    //  .call(drag);

    nodes.on("mouseover", function (d) {
      console.log('mouseover: ' + d3.select(this));
      var xPosition = parseFloat(d.x + scatter_radius);
      var yPosition = parseFloat(d.y);
      console.log(xPosition + ',' + yPosition);
      console.log('1. ' + d3.select(this));
      //Update the tooltip position and value

      d3.select("#tooltip_svg_01")
        .style("left", xPosition + "px")
        .style("top", yPosition + "px");
      d3.select("#value_tt_01")
        .text(d['x'] + ',' + d['y']);
      d3.select('#link_tt_01')
        .attr("href", "https://en.wikipedia.org/wiki/")
        .text(d['x'] + ',' + d['y']);

      //Show the tooltip
      d3.select(this).style("fill", 'red');
      d3.select("#tooltip_svg_01").style('opacity', 1).style("display", "block");

      //update the lower panel
      d3.select('#title_year')
        .text(d.name);
      d3.select('#connection')
        .text(d.connection);
      d3.select('#title_year')
        .attr("href", d.url);
      d3.select('#connected_add')
        .attr("data-id", d.id);

      //show the lower panel
      d3.select("#connected_panel").style('opacity', 1);
    })

  });

class SearchForm extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <div class="form-popup" id="myForm">
        <form action="/action_page.php" class="form-container">
          <div id="searchbar">
            <input type="text" placeholder="Search" name="query">
            <button type="button" class="btn search" onclick="searchMovie()">Find</button>
          </div>
    
          <label for="conn_dsc"></label>
          <input type="textarea" placeholder="Description" name="conn_dsc" required>
      
          <button type="submit" class="btn">Add</button>
          <button type="button" class="btn cancel" onclick="closeForm()">Close</button>
        </form>
      </div>
    `;
  }
}

function showSearchForm(elem) {
  movie1 = elem.dataset.id;
  document.getElementById("movie1").value = movie1;
  openForm();
}

function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

function addConnection(user_id) {
  document.location.href = `/add/${movie1}/${movie2}`;
}