const plot = document.querySelector("#plot");
const ctx = plot.getContext("2d");
const url_input = document.querySelector("#url-input");
const alert_div = document.querySelector("#alert");

const decoder = new TextDecoder("utf-8");

const OPAQUE = [
  "rgba(255, 99, 132, 1)",
  "rgba(54, 162, 235, 1)",
  "rgba(255, 206, 86, 1)",
  "rgba(75, 192, 192, 1)",
  "rgba(153, 102, 255, 1)",
  "rgba(255, 159, 64, 1)"
];

const TRANSLUSCENT = [
  "rgba(255, 99, 132, 0.2)",
  "rgba(54, 162, 235, 0.2)",
  "rgba(255, 206, 86, 0.2)",
  "rgba(75, 192, 192, 0.2)",
  "rgba(153, 102, 255, 0.2)",
  "rgba(255, 159, 64, 0.2)"
];

/* sample response json
const json = {
  generated_at: "2020-02-15 04:55:17",
  expires_in: "6 days, 9:17:27",
  url: "https://mastodon.technology/web/statuses/103657607384494793",
  instance: "mastodon.technology",
  id: 21344,
  multiple: false,
  choices: [
    {
      title: "Cate :cate:",
      points: [
        [4, 12],
        [5, 15],
        [6, 16],
        [8, 18]
      ]
    },
    {
      title: "Scremcat :scremcat:",
      points: [
        [4, 13],
        [5, 16],
        [8, 17],
        [9, 19]
      ]
    },
    {
      title: "Cringingcat :cringingcat:",
      points: [
        [4, 12],
        [5, 14],
        [7, 15],
        [8, 17]
      ]
    },
    {
      title: "Freddiecat :freddiecat:",
      points: [
        [4, 7],
        [6, 12],
        [8, 14],
        [9, 16]
      ]
    }
  ]
};
*/

const requestAnalysis = () => {
  console.log("requesting");
  const req = new Request("/analyze?url=" + url_input.value);
  alert_div.innerHTML = "Requesting...";
  fetch(req).then(res => {
    const reader = res.body.getReader();
    reader.read().then(({ done, value }) => {
      const text = decoder.decode(value);
      console.log(text);
      try {
        const json = JSON.parse(text);
        alert_div.innerHTML = "";
        console.log(json);
        makeChart(json);
      } catch {
        console.error(text);
        alert_div.innerHTML = text;
      }
    });
  });
};

const makeChart = json => {
  let datasets = [];
  for (let idx = 0; idx < json.choices.length; idx++) {
    const opt = json.choices[idx];
    let points = [];
    for (let i = 0; i < opt.points.length; i++) {
      points.push({ x: opt.points[i][0], y: opt.points[i][1] });
    }
    datasets.push({
      label: opt.title,
      data: points,
      backgroundColor: "rgba(0,0,0,0)",
      borderColor: OPAQUE[idx]
    });
  }
  console.log(datasets);
  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: json.choices,
      datasets
    }
  });
};
