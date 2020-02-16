const plot = document.querySelector("#plot");
const ctx = plot.getContext("2d");
const input = document.querySelector("#input");
const alert_div = document.querySelector("#alert");
const interval_picker = document.querySelector("#interval");
const interval_label = document.querySelector("#interval-label");

const decoder = new TextDecoder("utf-8");

const OPAQUE = [
  "rgba(255, 99, 132, 1)",
  "rgba(54, 162, 235, 1)",
  "rgba(255, 206, 86, 1)",
  "rgba(75, 192, 192, 1)",
  "rgba(153, 102, 255, 1)",
  "rgba(255, 159, 64, 1)"
];

/*
const parseSeconds = s => {
  d = Math.floor(s / 86400);
  h = Math.floor(s / 3600) - d * 24;
  m = Math.floor(s / 60) - d * 1440 - h * 60;
  s = s % 60;
  return `${d}d, ${h}:${m < 10 ? `0${m}` : m}:${s < 10 ? `0${s}` : s}`;
};
*/

/* sample response json
const json = {
  generated_at: "2020-02-15 07:47:52",
  expired: false,
  expires_in: "6 days, 6:24:53",
  key: "mastodon.technology_21344",
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
  const key = input.value.startsWith("https://") ? "url" : "key";
  const interval = interval_picker.value;
  const req = new Request(
    `/analyze?${key}=${input.value}&interval=${interval}`
  );
  alert_div.innerHTML = "Requesting...";
  fetch(req).then(res => {
    const reader = res.body.getReader();
    reader.read().then(({ done, value }) => {
      const text = decoder.decode(value);
      console.log(text);
      try {
        const json = JSON.parse(text);
        // proceed if response is valid json
        alert_div.innerHTML = "";
        console.log(json);
        makeChart(json);
        interval_label.hidden = true;
        interval_picker.hidden = true;
        const href = `${window.location.origin}/?key=${json.key}`;
        alert_div.innerHTML = `Use this link to view/share this pollspect: 
          <a href="${href}">${href}</a><br>
          <a href="${json.url}">View poll</a>`;

        if (json.expired) {
          alert_div.innerHTML +=
            "<br> This poll is expired. You are viewing archived data.";
        } else {
          alert_div.innerHTML +=
            "<br> This poll will expire in " + json.expires_in;
        }
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

  console.log(datasets);
  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: json.snapshots,
      datasets
    },
    options: {
      scales: { yAxes: [{ ticks: { beginAtZero: true } }] }
    }
  });
};

const parseParams = () => {
  const params_str = window.location.search;
  if (params_str.startsWith("?url=")) {
    input.value = params_str.replace("?url=", "");
    alert_div.innerHTML =
      "If you came from a link someone else posted, just click Pollspect. <br><br> If you typed the url manually and the URL contained a poll not yet in Pollspect's database, select Snapshot Interval before clicking Pollspect if you wish Pollspect to subscribe to the new poll. In this case, please be considerate for the admins of the instance. API requests cost. If the poll lasts longer than a day, select an interval no shorter than 30 minutes.";
  } else if (params_str.startsWith("?key=")) {
    input.value = params_str.replace("?key=", "");
    requestAnalysis();
  }
};

parseParams();
