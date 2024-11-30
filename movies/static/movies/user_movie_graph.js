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

      fetch('/search?q=' + userInput)
        .then(response => response.json())
        .then(movies => {
          search_results = movies;
          resultsHTML.style.display = "block";
          for (i = 0; i < 10; i++) {
            resultsHTML.innerHTML += "<li>" + movies[i].title + "</li>";
          }
        })
    }
  };

  document.getElementById("results").onclick = function (event) {
    const setValue = event.target.innerText;
    autocomplete.value = setValue;
    this.innerHTML = "";

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
  
  update_graph();
});

var scatter_radius = 10;
var search_results = [];
var user_graph;
var movie2;
var movie1;

function update_graph() {

	fetch(fetch_url)
	  .then(response => response.json())
	  .then(data => {
		user_graph = data.nodes;
		var c10 = d3.scale.category10();
		var svg = d3.select("svg");
		//.attr("width", graph_width)
		//.attr("height", graph_height);
		
		svg.selectAll('*').remove();

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
			.text(d.connection_description);
		  d3.select('#title_year')
			.attr("href", d.url);
		  d3.select('#connected_add')
			.attr("data-id", d.id);
		  d3.select('#connected_remove')
			.attr("data-url", d.remove_url);
		  d3.select('#connected_watchlist')
			.attr("href", d.want_to_watch_url);

		  //show the lower panel
		  d3.select("#connected_panel").style('opacity', 1);
		})

	  });
  
}

function showSearchForm(elem) {
  movie1 = elem.dataset.id;
  console.log(movie1);
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

function removeConnection() {
	const csrftoken = getCookie('csrftoken');
	remove_connection_url = event.currentTarget.dataset.url;
	
	fetch(remove_connection_url, {
	  method: "DELETE",
	  headers: { 'X-CSRFToken': csrftoken },
	  mode: 'same-origin',
	})
    .then(response => { 
      console.log(response);
	  update_graph();
	})
	.catch((error) => {
	  console.log(error);
	});
}

function trigger_button(movie_id, url, bool) {
  const csrftoken = getCookie('csrftoken');

  // we don't have a boolean

  fetch('') // we can have the url from the button
  // this is a POST request, so we pass the id. the url never changes

  // the response contains a boolean, so we switch the button accordingly
}

async function switch_status_in_db(movie_id, url, status)
{
  const csrftoken = getCookie('csrftoken');

  console.log("current status:" + status);

  let new_status = await fetch(url, {
    method: "POST",
    headers: { 'X-CSRFToken': csrftoken },
    mode: 'same-origin',
    body: JSON.stringify({
      id: movie_id,
      status: status,
    })
  })
    .then(response => response.json())
    .then(result => {
      console.log("Received from db: " + result.status);
      return result.status;
  })
  .catch((error) => {
    console.log(error);
  });

  console.log("new status:" + new_status);

  return new_status;
}

function button_toggle(handle, movie_id, url, status)
{
  if (status) {
    console.log("adding button_on");
    handle.classList.add('button_on');
  } else {
    console.log("removing button_on");
    handle.classList.remove('button_on');
  }

  handle.onclick = function () {
    console.log("new handle: " + handle); 
    watchlist_handler(handle, movie_id, url, status) };
}

async function watchlist_handler(handle, movie_id, url, status) {

  console.log("Event: " + event);
  console.log("handle:" + handle);

  let new_status = await switch_status_in_db(movie_id, url, status);

  button_toggle(handle, movie_id, url, new_status);

}

function watched(movie_id) {
  const csrftoken = getCookie('csrftoken');

  // this is ugly, but will have to do for now
  let movie = user_graph.filter(obj => {
    return obj.id === movie_id
  })[0];

  let watched = movie.watched;
  console.log(watched);

  fetch(movie.watched_url, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    mode: 'same-origin',
    body: JSON.stringify({
      watched: watched,
    })
  })
    .then(response => response.json())
    .then(result => {
      movie.watched = result.watched;
      button = document.getElementById("main_watched");
      console.log(result);
      if (result.watched) {
        button.className = "button_on";
      } else {
        button.className = "button_off";
      }
    })
    .catch((error) => {
      console.log(error);
    });

}

function renderRightMenu(right_menu_list_of_tuples) {
  const right_menu = document.getElementById("right_menu");
  const dropdown_menu = document.getElementById("right_dropdown");

  dropdown_menu.innerHTML = "";

  right_menu.style.display = "block";

  console.log(right_menu_list_of_tuples);

  for (var i = 0; i < right_menu_list_of_tuples.length; i++) {
    dropdown_menu.appendChild(createMenuItem(right_menu_list_of_tuples[i]));
  }

  return dropdown_menu;
}

function createMenuItem(item) {
  const name = item[0];
  const link = item[1];

  var newAnchor = document.createElement('a');
  newAnchor.classList.add('dropdown-item');
  newAnchor.setAttribute('href', link);
  newAnchor.innerHTML = name;

  var listItem = document.createElement('li');
  listItem.appendChild(newAnchor);

  return listItem;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}