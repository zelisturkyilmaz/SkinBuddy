let input1 = document.getElementById("productListInput1");
input1.addEventListener("input", async function () {
  let response = await fetch("/search?q=" + input1.value);
  let products = await response.json();
  let search = "";

  for (let i in products) {
    let name = products[i].brand + " " + products[i].name;
    search += '<option value="' + name + '" />';
  }

  document.getElementById("morningSearch").innerHTML = search;
});

let input2 = document.getElementById("productListInput2");
input2.addEventListener("input", async function () {
  let response = await fetch("/search?q=" + input2.value);
  let products = await response.json();
  let search = "";

  for (let i in products) {
    let name = products[i].fullname;
    search += '<option value="' + name + '" />';
  }

  document.getElementById("nightSearch").innerHTML = search;
});


const stars = document.getElementsByName("rating");

len = stars.length;


for (let i = 0; i < len; i++) {
  let mod = i % 5;
  stars[i].addEventListener("mouseover", function () {
    for (let x = mod; x >= 0; x--) {
      stars[i - x].className = "bi bi-star-fill";
    }
  });


  stars[i].addEventListener("mouseout", function () {
      for (let x = mod; x >= 0; x--) {
        stars[i - x].className = "bi bi-star";
      }
  });

};





/*
for (event of eventList) {
  star0.addEventListener(event, function() {
    star0.className = "bi bi-star-fill";
    star1.className = "bi bi-star";
    star2.className = "bi bi-star";
    star3.className = "bi bi-star";
    star4.className = "bi bi-star";
  })
};

for (event of eventList) {
  star1.addEventListener(event, function() {
    star0.className = "bi bi-star-fill";
    star1.className = "bi bi-star-fill";
    star2.className = "bi bi-star";
    star3.className = "bi bi-star";
    star4.className = "bi bi-star";
  })
};

for (event of eventList) {
  star2.addEventListener(event, function() {
    star0.className = "bi bi-star-fill";
    star1.className = "bi bi-star-fill";
    star2.className = "bi bi-star-fill";
    star3.className = "bi bi-star";
    star4.className = "bi bi-star";
  })
};

for (event of eventList) {
  star3.addEventListener(event, function() {
    star0.className = "bi bi-star-fill";
    star1.className = "bi bi-star-fill";
    star2.className = "bi bi-star-fill";
    star3.className = "bi bi-star-fill";
    star4.className = "bi bi-star";
  })
};

for (event of eventList) {
  star4.addEventListener(event, function() {
    star0.className = "bi bi-star-fill";
    star1.className = "bi bi-star-fill";
    star2.className = "bi bi-star-fill";
    star3.className = "bi bi-star-fill";
    star4.className = "bi bi-star-fill";
  })

};

for (star of starList) {
  star.addEventListener("mouseout", function() {
    star0.className = "bi bi-star";
    star1.className = "bi bi-star";
    star2.className = "bi bi-star";
    star3.className = "bi bi-star";
    star4.className = "bi bi-star";
  })
};

*/