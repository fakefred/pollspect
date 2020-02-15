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

const parseSeconds = s => {
  d = Math.floor(s / 86400);
  h = Math.floor(s / 3600) - d * 24;
  m = Math.floor(s / 60) - d * 1440 - h * 60;
  s = s % 60;
  return `${d}d, ${h}:${m < 10 ? `0${m}` : m}:${s < 10 ? `0${s}` : s}`;
};

/* sample response json
const json = {
  generated_at: "2020-02-15 07:47:52",
  expires_in: "6 days, 6:24:53",
  url: "https://mastodon.technology/web/statuses/103657607384494793",
  instance: "mastodon.technology",
  id: 21344,
  multiple: false,
  snapshots: [4, 8438, 8450, 8471, 15313, 15439, 15557, 15681, 16064],
  choices: [
    { title: "Cate :cate:", votes: [1, 1, 1, 1, 3, 3, 3, 3, 3] },
    { title: "Scremcat :scremcat:", votes: [1, 1, 1, 1, 1, 1, 1, 1, 1] },
    { title: "Cringingcat :cringingcat:", votes: [1, 1, 1, 1, 1, 1, 1, 1, 1] },
    { title: "Freddiecat :freddiecat:", votes: [0, 0, 0, 0, 1, 1, 1, 1, 1] }
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
    datasets.push({
      label: opt.title,
      data: opt.votes,
      backgroundColor: "rgba(0,0,0,0)",
      borderColor: OPAQUE[idx],
      cubicInterpolationMode: "monotone"
    });
  }
  snapshots = [];
  json.snapshots.forEach(v => {
    snapshots.push(parseSeconds(v));
  });
  console.log(datasets);
  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: snapshots,
      datasets
    }
  });
};
