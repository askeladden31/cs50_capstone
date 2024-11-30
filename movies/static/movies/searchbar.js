var search_results = [];

// fetches the movies from the database
function fetchMovies(userInput) {
	
	let search_results = fetch('/search?q=' + userInput)
        .then(response => response.json())
				
	return search_results;
}

document.addEventListener('DOMContentLoaded', function () {
	
  //const searchBar = document.getElementById("s_bar");
  //const searchResults = document.getElementById("s_results");
  // DOM elements with IDs are accessible in JavaScript as global variables
  
  let timer;

  s_bar.oninput = function () {
	  
	clearTimeout(timer);
    const userInput = this.value;
    s_results.innerHTML = "";
	
    if (userInput.length > 2) {
		
	  timer = setTimeout(async function() {
		  
		search_results = await fetchMovies(userInput)	  
		console.log(search_results);
		for (i = 0; i < search_results.length; i++) {
		  s_results.innerHTML += "<li id='" + search_results[i].id + "'>" + search_results[i].title + "</li>";
		}
		
	  }, 500)
    }
    
  };

  s_results.onclick = function (event) {
    const foundValue = event.target.innerText;
    const foundId = event.target.id;
    s_bar.value = foundValue;
    this.innerHTML = "";

    // we know the id now
    // can fetch the data

    fetch(`/right_menu_api/${foundId}`)
      .then(response => response.json())
      .then(res => {

        console.log(res);
		
		right_menu = renderRightMenu(res.right_menu)

        if (Object.keys(res.watchlists).length > 0) {

          watched_button = right_menu.appendChild(createMenuItem(['Watched', '#']));
          wanna_watch_button = right_menu.appendChild(createMenuItem(['Wanna watch', '#']));

          // watched_button.firstChild.setAttribute("onclick", "watched(" + foundId + ")");

          watched_button.onclick = function () {
            watchlist_handler(this, foundId, res.watched_url, res.watched);
          };

          wanna_watch_button.onclick = function () {
            console.log("this from inside anon func: " + this); 
            watchlist_handler(this, foundId, res.wannawatch_url, res.wannawatch);
          };

          button_toggle(watched_button, foundId, res.watched_url, res.watched);
          button_toggle(wanna_watch_button, foundId, res.wannawatch_url, res.wannawatch);
        }
      })
  }
  
})


function substitute_searchbar() {
  s_bar = document.getElementById('s_bar');
  s_bar.style.display = 'none';

  login_form = createLoginForm();

  s_bar.replaceWith(login_form);

  right_menu = renderRightMenu([['Login','#'],['Cancel','#']]);

};

async function switch_status_in_db(movie_id, url, status)
{
  const csrftoken = getCookie('csrftoken');

  console.log("current status: " + status);

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
  console.log("handle: " + handle);

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